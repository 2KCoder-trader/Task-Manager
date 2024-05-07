from ast import main
from datetime import datetime
# import curses
def get_name():
    name = input('Enter the task name: ')
    if name == '':
        print('Name cannot be empty')
        name = get_name()
    return name
def get_desc():
    desc = input('Enter the task description: ')
    if desc == '':
        desc = 'No description'
    return desc
def get_deadline():
    deadline = input('Enter the task deadline(M D (H) (M)): ')
    if deadline == '':
        deadline = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    elif len(deadline.split()) == 2:
        deadline = datetime.strptime(deadline, '%m %d').replace(hour=23, minute=59, second=0, microsecond=0).replace(year=datetime.now().year)
    elif len(deadline.split()) == 3:
        deadline = datetime.strptime(deadline, '%m %d %H').replace(year=datetime.now().year)
    elif len(deadline.split()) == 4:
        deadline = datetime.strptime(deadline, '%m %d %H %M').replace(year=datetime.now().year)
    else:
        print('Invalid deadline format')
        deadline = get_deadline()
    if deadline < datetime.now():
        print(deadline," < ",datetime.now())
        print('Deadline must be in the future')
        deadline = get_deadline()
    return deadline
def get_type():
    print('Select the task type(school, DOH, career, game, other):')
    print('1. School')
    print('2. DOH')
    print('3. Career')
    print('4. Game')
    print('5. Other')
    type = input('Enter the number of the type: ')
    if type == '1':
        type = 'school'
        priority = 3
    elif type == '2':
        type = 'DOH'
        priority = 2
    elif type == '3':
        type = 'career'
        priority = 3
    elif type == '4':
        type = 'game'
        priority = 0
    elif type == '5':
        type = 'other'
        priority = 1
    else:
        print('Invalid type')
        type,priority = get_type()
    
    return type,priority

    
# # define the menu function
# def menu(title, classes, color='white'):
#   # define the curses wrapper
#   def character(stdscr,):
#     attributes = {}
#     # stuff i copied from the internet that i'll put in the right format later
#     icol = {
#       1:'red',
#       2:'green',
#       3:'yellow',
#       4:'blue',
#       5:'magenta',
#       6:'cyan',
#       7:'white'
#     }
#     # put the stuff in the right format
#     col = {v: k for k, v in icol.items()}

#     # declare the background color

#     bc = curses.COLOR_BLACK

#     # make the 'normal' format
#     curses.init_pair(1, 7, bc)
#     attributes['normal'] = curses.color_pair(1)


#     # make the 'highlighted' format
#     curses.init_pair(2, col[color], bc)
#     attributes['highlighted'] = curses.color_pair(2)


#     # handle the menu
#     c = 0
#     option = 0
#     while c != 10:

#         stdscr.erase() # clear the screen (you can erase this if you want)

#         # add the title
#         stdscr.addstr(f"{title}\n", curses.color_pair(1))

#         # add the options
#         for i in range(len(classes)):
#             # handle the colors
#             if i == option:
#                 attr = attributes['highlighted']
#             else:
#                 attr = attributes['normal']
            
#             # actually add the options

#             stdscr.addstr(f'> ', attr)
#             stdscr.addstr(f'{classes[i]}' + '\n', attr)
#         c = stdscr.getch()

#         # handle the arrow keys
#         if c == curses.KEY_UP and option > 0:
#             option -= 1
#         elif c == curses.KEY_DOWN and option < len(classes) - 1:
#             option += 1
#     return option
#   return curses.wrapper(character)
# print(f"output:", menu('TEST', ['this will return 0','this will return 1', 'this is just to show that you can do more options then just two'], 'blue'))