import argparse
import itertools


def cli_args():
    parser = argparse.ArgumentParser(description="""Sudoer file to be parsed""", epilog="Red + Yellow + Blue is Black")
    parser.add_argument("sudoer_file", metavar="sudoer file", help="sudoer file")
    return parser.parse_args()


def parse(sudoer_f):
    user_alias = {}
    cmd_alias = {}
    runas_alias = {}
    n = 0
    result = []
    with open(sudoer_f) as sudoer:

        for l in sudoer:
            n += 1
            #print(n)
            if l.startswith('#') or not l.strip():
                continue
            content = l.strip('\r\n')
            while content.endswith('\\'):
                content = content.rstrip('\\')
                content += next(sudoer).rstrip('\r\n').strip()
                n += 1
                #print(n)
            #print(content)

            if l.startswith('User_Alias'):
                key_value = content[10:].split('=', 1)
                if len(key_value) != 2:
                    raise Exception('Invalid line at ' + str(n) + ': ' + content)
                key = key_value[0].strip()
                value = [item.strip() for item in key_value[1].split(',')]
                user_alias[key] = value
                # print('User Alias ' + key + ': ' + str(value))
            elif content.startswith('Cmnd_Alias'):
                key_value = content[10:].split('=', 1)
                if len(key_value) != 2:
                    raise Exception('Invalid line at ' + str(n) + ': ' + content)
                key = key_value[0].strip()
                value = [item.strip() for item in key_value[1].split(',')]
                cmd_alias[key] = value
                # print('Command Alias ' + key + ': ' + str(value))
            # Actual sudo lines
            elif content.startswith('Runas_Alias'):
                key_value = content[11:].split('=', 1)
                if len(key_value) != 2:
                    raise Exception('Invalid line at ' + str(n) + ': ' + content)
                key = key_value[0].strip()
                value = [item.strip() for item in key_value[1].split(',')]
                runas_alias[key] = value

            elif 'ALL' in content:
                splited = content.strip('\r\n').split()
                if len(splited) < 3 or len(splited) == 3 and not splited[1].endswith(')'):
                    print('Invalid actual line at ' + str(n) + ': ' + l)
                    continue
                user = splited[0]
                if user in user_alias.keys():
                    users = user_alias[user]
                else:
                    users = [user]
                # parsing sudo user
                # ALL=( Rorods)
                if 'ALL' not in splited[1] or ')' not in splited[1]:
                    print('Invalid actual line at ' + str(n) + ': ' + l)
                    continue
                nn = 1
                sudo_user_l = splited[1]
                while not sudo_user_l.endswith(')') and nn < len(splited):
                    nn += 1
                    sudo_user_l += splited[nn]
                sudo_users = [item.strip() for item in sudo_user_l[5:-1].split(',')]
                real_runas = []
                for r in sudo_users:
                    if r in runas_alias.keys():
                        real_runas.extend(runas_alias[r])
                    else:
                        real_runas.append(r)
                # parsing command
                if splited[nn+1] == 'NOPASSWD:':
                    nn += 1
                command = splited[nn+1].strip()
                if len(splited) == nn + 2:
                    commands = [command]
                else:
                    for i in range(nn + 2, len(splited) - 1):
                        command += splited[i]
                    commands = [item.strip() for item in command.split(',')]
                real_command = []
                for c in commands:
                    if c in cmd_alias.keys():
                        real_command.extend(cmd_alias[c])
                    else:
                        real_command.append(c)
                # print(str(users), str(sudo_users), str(real_command))
                result.extend(itertools.product(users, real_runas, real_command))
    with open(sudoer_f + '.csv', 'w+') as output:
        for i in result:
            print('{0},{1},{2}'.format(i[0], i[1], i[2]), file=output)


if __name__ == '__main__':
    args = cli_args()
    parse(args.sudoer_file)
