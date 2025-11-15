#!/usr/bin/env python3

import argparse
import subprocess
import sys


def identificar_backend():
  
    try:
        subprocess.run(['nft', 'list', 'ruleset'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 'nftables'
    except (FileNotFoundError, subprocess.CalledProcessError):
       
        try:
            subprocess.run(['sudo','iptables', '-L'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return 'iptables'
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Erro: Nenhum backend de firewall (nftables ou iptables) encontrado/ativo.", file=sys.stderr)
            sys.exit(1)


def construir_comando_delete(backend, acao, protocolo, porta, source=None):
    
    
    comando_delete = ""
    chain = "INPUT"
    
    if backend == 'iptables':
        source_opt = f"-s {source}" if source else ""
        target = "ACCEPT" if acao == 'allow' else "DROP"
        comando_delete = f"iptables -D {chain} {source_opt} -p {protocolo} --dport {porta} -j {target}"

    elif backend == 'nftables':
        tabela = "filter"
        source_opt = f"ip saddr {source}" if source else ""
        target = "accept" if acao == 'allow' else "drop"
        
        comando_delete = f"nft delete rule inet {tabela} {chain.lower()} {source_opt} {protocolo} dport {porta} {target}"

    return [comando_delete] 

def construir_comando(backend, acao, protocolo, porta, source=None):
    
    conntrack_rule = ""
    if backend == 'iptables':
        conntrack_rule = f"iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT"
    elif backend == 'nftables':
        conntrack_rule = f"nft add rule inet filter input ct state established,related accept"
        
    comando_regra = ""
    
    chain = "INPUT"
    
    if backend == 'iptables':
        source_opt = f"-s {source}" if source else ""
        if acao == 'allow':
            comando_regra = f"iptables -A {chain} {source_opt} -p {protocolo} --dport {porta} -j ACCEPT"
        elif acao == 'drop':
            comando_regra = f"iptables -A {chain} {source_opt} -p {protocolo} --dport {porta} -j DROP"

    elif backend == 'nftables':
        tabela = "filter"
        source_opt = f"ip saddr {source}" if source else ""
        
        if acao == 'allow':
            comando_regra = f"nft add rule inet {tabela} {chain.lower()} {source_opt} {protocolo} dport {porta} accept"
        elif acao == 'drop':
            comando_regra = f"nft add rule inet {tabela} {chain.lower()} {source_opt} {protocolo} dport {porta} drop"

    return [conntrack_rule, comando_regra] if conntrack_rule else [comando_regra]


def inicializar_nftables():
    print("Inicializando estruturas básicas do nftables...")
    subprocess.run(['sudo', 'nft', 'add', 'table', 'inet', 'filter'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['sudo', 'nft', 'add', 'chain', 'inet', 'filter', 'input', 
                    '{', 'type', 'filter', 'hook', 'input', 'priority', '0', '\;', 'policy', 'drop', '\;','}'], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def executar_comando(comando):
   
    full_command = ['sudo'] + comando.split()
    print(f"Executando: {' '.join(full_command)}")
    try:
        subprocess.run(full_command, check=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
        print("Operação concluída com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"AVISO/ERRO ao executar a operação:\n{e.stderr.decode()}", file=sys.stderr)



def cmd_allow(args, backend):
    
    if backend == 'nftables':
        inicializar_nftables()
        
    comandos = construir_comando(backend, 'allow', args.protocolo, args.porta, args.source)
    for cmd in comandos:
        if cmd:
            executar_comando(cmd)

def cmd_drop(args, backend):

    if backend == 'nftables':
        inicializar_nftables()
        
    comandos = construir_comando(backend, 'drop', args.protocolo, args.porta, args.source)
    for cmd in comandos:
        if cmd:
            executar_comando(cmd)

def cmd_delete(args, backend):
    
    comandos = construir_comando_delete(backend, args.acao, args.protocolo, args.porta, args.source)
    
    print(f"\n--- Tentando remover regra ({backend.upper()}) ---")
    for cmd in comandos:
        if cmd:
            executar_comando(cmd)


def cmd_list(args, backend):

    print(f"\n--- Lista de Regras ({backend.upper()}) ---")
    if backend == 'iptables':
        executar_comando("iptables -L -v -n")
    elif backend == 'nftables':
        executar_comando("nft list ruleset")

def cmd_flush(args, backend):
    
    print(f"\n--- Removendo todas as regras ({backend.upper()}) ---")
    if input(f"Tem certeza que deseja limpar TODAS as regras do {backend}? (s/N): ").lower() != 's':
        print("Operação cancelada.")
        return
        
    if backend == 'iptables':
        executar_comando("iptables -F")
        executar_comando("iptables -Z")
        executar_comando("iptables -P INPUT ACCEPT")
        executar_comando("iptables -P FORWARD ACCEPT")
        executar_comando("iptables -P OUTPUT ACCEPT")
        executar_comando("iptables -t nat -F")
    elif backend == 'nftables':
        executar_comando("nft flush ruleset")
        
    print("Regras limpas. Recomenda-se reiniciar o serviço de firewall para garantir o estado inicial.")



def main():

    backend = identificar_backend()
    print(f"Backend de firewall detectado: {backend.upper()}")
    
    parser = argparse.ArgumentParser(
        description="netcli: Utilitário para gerenciar iptables/nftables com sintaxe unificada.",
        epilog=f"Usando o backend: {backend.upper()}"
    )

    subparsers = parser.add_subparsers(dest='comando', required=True)

    parser_allow = subparsers.add_parser('allow', help='Permite tráfego (ACCEPT) para uma porta e protocolo.')
    parser_allow.add_argument('protocolo', choices=['tcp', 'udp'], help='Protocolo de rede (tcp ou udp).')
    parser_allow.add_argument('porta', type=int, help='Porta de destino (ex: 80, 443, 22).')
    parser_allow.add_argument('--source', help='Endereço IP ou rede de origem (opcional).')
    parser_allow.set_defaults(func=cmd_allow, backend=backend)

    parser_drop = subparsers.add_parser('drop', help='Bloqueia tráfego (DROP) para uma porta e protocolo.')
    parser_drop.add_argument('protocolo', choices=['tcp', 'udp'], help='Protocolo de rede (tcp ou udp).')
    parser_drop.add_argument('porta', type=int, help='Porta de destino (ex: 80, 443, 22).')
    parser_drop.add_argument('--source', help='Endereço IP ou rede de origem (opcional).')
    parser_drop.set_defaults(func=cmd_drop, backend=backend)
    
    parser_delete = subparsers.add_parser('delete', help='Remove uma regra específica (é necessário saber se era "allow" ou "drop").')

    parser_delete.add_argument('acao', choices=['allow', 'drop'], help='A ação da regra a ser removida (allow = ACCEPT; drop = DROP).')
    parser_delete.add_argument('protocolo', choices=['tcp', 'udp'], help='Protocolo de rede (tcp ou udp).')
    parser_delete.add_argument('porta', type=int, help='Porta de destino (ex: 80, 443, 22).')
    parser_delete.add_argument('--source', help='Endereço IP ou rede de origem (opcional).')
    parser_delete.set_defaults(func=cmd_delete, backend=backend)

    parser_list = subparsers.add_parser('list', help='Lista as regras do firewall.')
    parser_list.set_defaults(func=cmd_list, backend=backend)
    
    parser_flush = subparsers.add_parser('flush', help='Remove todas as regras do firewall (cuidado!).')
    parser_flush.set_defaults(func=cmd_flush, backend=backend)

   
    args = parser.parse_args()
    args.func(args, args.backend)

if __name__ == '__main__':
    main()