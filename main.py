
import argparse
import subprocess
import sys




def identificar_backend():
    
    try:
        subprocess.run(['sudo', 'nft', 'list', 'ruleset'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 'nftables'
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass 

    try:
        subprocess.run(['sudo', 'iptables', '-L'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 'iptables'
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass 
        
    print("ERRO DE PERMISSÃO/DETECÇÃO:", file=sys.stderr)
    print("Não foi possível encontrar ou executar 'nft' ou 'iptables'.", file=sys.stderr)
    print("Certifique-se de que o programa está sendo executado por um usuário com permissão 'sudo'.", file=sys.stderr)
    sys.exit(1)



def main():

    backend = identificar_backend()
    print(backend)




if __name__ == '__main__':
    main()