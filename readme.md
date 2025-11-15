# NETCLI: Um utilitário em linha de comando para gestão unificada de firewalls em ambientes linux

Utilitário Python para gerenciar regras de firewall em sistemas Linux usando uma sintaxe de comando única e simplificada.

Este script detecta automaticamente o *backend* de firewall ativo e traduz seus comandos unificados para o formato nativo do sistema.

---

# Bibliotecas utilizadas

### 1. argparse

Esta é a biblioteca principal para a construção da Interface de Linha de Comando. Ela interpreta e processa os argumentos passado pelo usuário.



### 2. subprocess

Permite que o script Python execute comandos externos do sistema.

### 3. sys

Principalmente utilizada para gerenciar a saída e o encerramento do script.

---

## Recursos Principais

* **Suporte:** O script possui suporte para  `iptables` e `nftables`.
* **Detecção Automática:** O programa se adapta ao firewall ativo no seu sistema.
* **Ações Chave:** Permite (`allow`), bloqueia (`drop`), lista (`list`), deleta(`delete`) e limpa (`flush`) regras.

---

## Instalação e Configuração

Para usar o `netcli` como um comando global no seu sistema, siga estes passos:

### 1. Clonar o Repositório

Baixe os arquivos do projeto para sua máquina local:

```bash
git clone git@github.com:filipevmimbarcas/projeto-redes-de-computadores.git
cd projeto-redes-de-computadores
```

### 2. Tornar executável

Defina a permissão de execução no arquivo principal (main.py):

```
chmod +x main.py
```

### 3. Instalar como Comando Global

Mova o script para o diretório /usr/local/bin (que está no seu $PATH) e o renomeie para netcli. Isso permite que você o execute de qualquer lugar:

```bash
 sudo mv main.py /usr/local/bin/netcli
```

### Guia de uso do netcli

O comando principal é `netcli`, seguido de uma das quatro ações disponíveis.


### 1. Permitir tráfego

Adiciona uma regra de permissão para uma porta e protocolo.

Exemplo 1: 

```bash
sudo netcli allow tcp 22
```

Adiciona uma regra de permissão com restrição de origem.

Exemplo 2:

```bash
sudo netcli allow tcp 80 --source 192.168.1.50
```

### 2. Bloquear tráfego

Adiciona uma regra de bloqueio

Exemplo 1: Bloquear a porta 25
```bash
sudo netcli drop tcp 25
```

Exemplo 2: bloquear tudo de uma rede especifica

```bash
sudo netcli drop tcp 80 --source 192.168.20.0/24
```

### 3. Listar regras 

Exibe todas as regras do firewall detectado.

```bash
ncli list
```


### 4. Deleta regras

Deleta uma regra especifica

```bash
delete drop tcp 22 --source 192.168.20.0/24
```

### 4. Limpar todas as regras

Remove todas as regras do firewall

```bash
sudo netcli flush
```



