import sys
import json
import time
import socket
import typing

from threading import Thread

if __name__ != "__main__":
    sys.exit()


'''
=================================================================
-- Declarar constantes
=================================================================
'''

ENABLE_DEBUG = True

PORT = 55151

ARG_NAME_ADDR = '--addr'
ARG_NAME_PI = '--update-period'
ARG_NAME_STARTUP = '--startup-commands'

COMMAND_INIT = 'init'
COMMAND_QUIT = 'quit'
COMMAND_HELP = 'help'

COMMAND_ADD = 'add'
COMMAND_DEL = 'del'
COMMAND_TRACE = 'trace'
COMMAND_ROUTER_LIST = [COMMAND_ADD, COMMAND_DEL, COMMAND_TRACE]


'''
=================================================================
-- Declarar funcoes auxiliares ----------------------------------
=================================================================
'''

'''
    Funcao auxiliar para depuracao.
'''
def print_debug(dbg_text: str) -> None:
    if ENABLE_DEBUG:
        print(dbg_text)

'''
    Exibe instrucoes de uso de comando: Inicializacao do programa
'''
def print_instructions_init() -> None:
    print('\nInitialization command formats:')
    print('\t- 01: "router.py <IP: string> <pi: float>"')
    print('\t- 02: "router.py <IP: string> <pi: float> <startup_file: string>')
    print('\t- 03: "router.py --addr <IP: string> --update-period <pi: float>')
    print('\t- 04: "router.py --addr <IP: string> --update-period <pi: float> --startup-commands <startup_file: string>')

'''
    Exibe instrucoes de uso de comando: Adicao de roteaodr.
'''
def print_instructions_add() -> None:
    print('\n' + COMMAND_ADD + ' command format:')
    print('\t"router.py ' + COMMAND_ADD + ' <IP: string> <weight: int>"')

'''
    Exibe instrucoes de uso de comando: Remocao de roteaodr.
'''
def print_instructions_del() -> None:
    print('\n' + COMMAND_DEL + ' command format:')
    print('\t"router.py ' + COMMAND_DEL + ' <IP: string>')

'''
    Exibe instrucoes de uso de comando: Rastreamento de roteaodr.
'''
def print_instructions_trace() -> None:
    print('\n' + COMMAND_TRACE + ' command format:')
    print('\t"router.py ' + COMMAND_TRACE + ' <IP: string>')

'''
    Centraliza chamadas para exibicao de instrucoes de uso.
'''
def print_instructions(help_command: str) -> None:

    print('\nInstructions:')

    if (not help_command or help_command == COMMAND_INIT):
        print_instructions_init()
    if (not help_command or help_command == COMMAND_ADD):
        print_instructions_add()
    if (not help_command or help_command == COMMAND_DEL):
        print_instructions_del()
    if (not help_command or help_command == COMMAND_TRACE):
        print_instructions_trace()

'''
    Avalia 01 string generica & retorna sua versao de IP caso represente 01 IP valido.
'''
def get_ip_version(addr: str) -> typing.Union[int, bool]:
    try:

        # V4
        try:
            socket.inet_pton(socket.AF_INET, addr)
            return 4

        # V6
        except socket.error:
            socket.inet_pton(socket.AF_INET6, addr)
            return 6

    except socket.error:
        return False

'''
    Valida string quanto a representar um endereco IP valido.
'''
def validate_ip(addr: str, version: int = 4) -> bool:
    if (not version in [4, 6]):
        raise ValueError('Invalid IP version for validation')
    return version == get_ip_version(addr)

'''
    Valida linha para comando de exibir instrucoes.
'''
def validate_command_help(command_args: list) -> None:

    argsc = len(command_args)
    if (argsc > 2):
        raise IOError(COMMAND_HELP + ' command takes exactly 01 or 02 arguments')

    if (argsc == 2 and not command_args[1] in COMMAND_ROUTER_LIST):
        raise IOError('Argument 1 is not a valid router command')

'''
Valida & retorna parametros de linha de comando.

'''
def get_cli_params() -> object:

    # Detecta formato do comando de incializacao de acordo com a quantidade de argumentos recebidos
    argsc = len(sys.argv)
    command_format = 0
    
    if (argsc <= 5):
        command_format = argsc - 2
    elif (argsc == 7):
        command_format = 4

    if (not command_format in [1, 2, 3, 4]):
        raise IOError('Invalid number of arguments')

    addr = ''
    pi = 0
    startup_path = ''

    # Trata caso de parametros nominais
    
    if (command_format in [3, 4]):

        if (sys.argv[1] != ARG_NAME_ADDR):
            raise IOError('Invalid argument at position 1. (Was it supposed to be "' + ARG_NAME_ADDR + '" ?)')
        if (sys.argv[3] != ARG_NAME_PI):
            raise IOError('Invalid argument at position 3. (Was it supposed to be "' + ARG_NAME_PI + '" ?)')
        if (command_format == 4 and sys.argv[5] != ARG_NAME_STARTUP):
            raise IOError('Invalid argument at position 5. (Was it supposed to be "' + ARG_NAME_STARTUP + '" ?)')

        addr = sys.argv[2]
        pi = sys.argv[4]

        if (command_format == 4):
            startup_path = sys.argv[6]
            if (not startup_path):
                raise IOError('Argument ' + ARG_NAME_STARTUP + ' requires a file path')

    # Trata caso de parametros implicitos
    else:
        pi = sys.argv[2]
        addr = sys.argv[1]
        if (argsc > 3):
            startup_path = sys.argv[3]

    # Validar endereco
    if (not addr):
        raise IOError('Address is required')
    if (not validate_ip(addr)):
        raise IOError('Invalid address')
    
    # Validar PI
    if (not pi):
        raise IOError('Update period (pi) is required')

    try:
        pi = float(pi)
    except ValueError:
        raise IOError('Invalid update period (must be a number)')

    '''
        TODO: 2021-08-04 - Validar path do arquivo
    '''

    class return_data: pass
    return_data.addr = addr
    return_data.pi = pi
    return_data.startup_path = startup_path
    return return_data

'''
    Avalia & retorna parametros de linha do comando: Add roteador.
'''
def get_command_data_add(command_args: list) -> object:
    
    argsc = len(command_args)

    try:
        
        if (argsc != 3):
            raise IOError(COMMAND_ADD + ' command takes exactly 03 arguments')

        class return_data: pass

        return_data.router_addr = command_args[1]
        if (not validate_ip(return_data.router_addr)):
            raise IOError('Invalid IP address')
        
        return_data.router_weight = int(command_args[2])
        return return_data

    except IOError as failure:
        print_instructions(COMMAND_ADD)
        raise failure

'''
    Avalia & retorna parametros de linha do comando: Remover roteador.
'''
def get_command_data_del(command_args: list) -> object:
    
    argsc = len(command_args)

    try:
        
        if (argsc != 2):
            raise IOError(COMMAND_DEL + ' command takes exactly 02 arguments')

        class return_data: pass
        return_data.router_addr = command_args[1]
        return return_data

    except IOError as failure:
        print_instructions(COMMAND_DEL)
        raise failure

'''
    Avalia & retorna parametros de linha do comando: Rastrear roteador.
'''
def get_command_data_trace(command_args: list) -> object:
    
    argsc = len(command_args)

    try:
        
        if (argsc != 2):
            raise IOError(COMMAND_TRACE + ' command takes exactly 02 arguments')

        class return_data: pass
        return_data.router_addr = command_args[1]
        return return_data

    except IOError as failure:
        print_instructions(COMMAND_TRACE)
        raise failure

'''
    Avalia & retorna parametros de linha de 01 comando generico.
'''
def get_command_data(command_line: str) -> object:

    command_args = command_line.split()
    command_type = command_args[0]

    if (command_type == COMMAND_ADD):
        parsed_args = get_command_data_add(command_args)
    elif (command_type == COMMAND_DEL):
        parsed_args = get_command_data_del(command_args)
    elif (command_type == COMMAND_TRACE):
        parsed_args = get_command_data_trace(command_args)

    else:

        class parsed_args: pass
        
        if (command_type == COMMAND_HELP):
            validate_command_help(command_args)
            parsed_args.help_command = command_args[1] if len(command_args) == 2 else None

    parsed_args.command = command_type
    return parsed_args

'''
    Executa comando: Exibir instrucoes.
'''
def execute_command_help(command_type: str) -> None:
    return print_instructions(command_type)

'''
    Executa comando: Add roteador na rede.
'''
def execute_command_add(address: str, weight: int) -> None:
    table_routes[address] = { 'weight': weight, 'periods': 0 }

'''
    Executa comando: Remover roteador na rede.
'''
def execute_command_del(address: str) -> None:
    if (table_routes[address]):
        table_routes.pop(address)

'''
    Executa comando: Rastrear 01 roteador na rede.
'''
def execute_command_trace(address: str) -> None:
    raise NotImplemented('function execute_command_trace() is yet to be implemented :(')

'''
    Calcula & retorna distancias entre cada vizinho & este vizinho.
'''
def get_update_distances(src_addr: str, destination_addr: str, destination_distance: int) -> dict:

    distances = { src_addr: destination_distance }

    for neighbor_addr, neighbor_data in table_routes.items():
        if (neighbor_addr != destination_addr):
            distances[neighbor_addr] = destination_distance + neighbor_data['weight']

    return distances

'''
    TODO: 2021-08-05 - ADD Descricao
'''
def thread_update_send(pi: float, addr: str, sock: socket.socket) -> None:

    '''
        TODO: 2021-08-05 - Checar necessidade de manter 'i'
    '''

    i: int = 0

    while True:

        i = i + 1

        for neighbor_addr, neighbor_data in table_routes.items():
            # print('inside thread...', i, neighbor_addr, neighbor_data)

            msg_update = {
                'type': 'update',
                'source': addr,
                'destination': addr,
                'distances': get_update_distances(addr, neighbor_addr, neighbor_data['weight'])
            }

            sock.sendto(json.dumps(msg_update).encode(), (neighbor_addr, PORT))

        time.sleep(pi)


'''
=================================================================
-- Loop principal -----------------------------------------------
=================================================================
'''


'''
    TODO: 2021-08-04 - Abrir trhead para atualizacao periodica da tabela de rotas
'''

print('\nRunning...')
print('  Type "' + COMMAND_HELP + ' (' + '|'.join([COMMAND_ADD, COMMAND_DEL, COMMAND_TRACE]) + ')?" for instructions;')
print('  Type "' + COMMAND_QUIT + '" to quit;')

cli_arguments = None
table_routes = {}

try:

    cli_arguments = get_cli_params()

    # Criar roteador
    routerFD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    routerFD.bind((cli_arguments.addr, PORT))

    # Abrir thread para envio de msgs de update
    thread_update = Thread(target=thread_update_send, args=(cli_arguments.pi, cli_arguments.addr, routerFD))
    thread_update.start()

    while (True):
        
        # Le comando via CLI
        command_line = input('\nEnter command: ')

        try:
            command_data = get_command_data(command_line)
        except IOError as failure:
            print('Invalid input! >.<\"')
            print(failure)
            continue

        # Executa comando solicitado
        if (command_data.command == COMMAND_QUIT):
            break

        if (command_data.command == COMMAND_HELP):
            execute_command_help(command_data.help_command)

        elif (command_data.command == COMMAND_ADD):
            execute_command_add(command_data.router_addr, command_data.router_weight)

        elif (command_data.command == COMMAND_DEL):
            execute_command_del(command_data.router_addr)

        '''
            TODO: 2021-08-04 - Tratar comando 'trace'
        '''

except Exception as failure:
    
    print("\n\n-- FALHA ---------\n", failure)
    print('\n')

    if (cli_arguments == None):
        print_instructions_init()

    if (ENABLE_DEBUG):
        raise failure

finally:
    routerFD.close()
    print("\n-- THE END --\n")
