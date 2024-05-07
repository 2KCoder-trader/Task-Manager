from hmac import new
from math import nan
import time
import pandas as pd
from tabulate import tabulate
import numpy as np
from datetime import datetime, timedelta
import os
from colorama import Fore, Back, Style
import sys
import ui_entries
import signal
def update_tasks():
    df = pd.read_csv('tasks.csv',index_col=0)
    df['wait_time'] = pd.to_datetime(df['wait_time'])
    for index, row in df.iterrows():
        if row['status'] == 2:
            if datetime.now() > row['wait_time']:
                df.loc[index, 'status'] = 1
    df = df.sort_values(by=['status'],ascending=True)
    df = df.reset_index(drop=True)
    df.to_csv('tasks.csv')

def handler(signum, frame):
    raise Exception("Timeout!")


def delete_task():
    print('Deleting a task')
    df = pd.read_csv('tasks.csv',index_col=0)
    df = df[df['status'] != 3]
    print(tabulate(df[['name','status','deadline']],headers='keys',tablefmt='grid'))
    df = pd.read_csv('tasks.csv',index_col=0)
    task_index = input('Enter the index of the task you would like to delete: ')
    task = df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','description','status','deadline','type']],headers='keys',tablefmt='grid'))
    confirm = input('Are you sure you want to delete this task? (y/n): ')
    if confirm == 'y':
        df = df.drop(int(task_index))
        df.to_csv('tasks.csv')
    elif confirm == 'n':
        return
    else:
        print('Invalid input')
        delete_task()
    update_tasks()

def create_task():
    print('Creating a new task')
    name = ui_entries.get_name()
    desc = ui_entries.get_desc()
    deadline = ui_entries.get_deadline()
    type, priority = ui_entries.get_type()
    if type != 'game':
        task = {'name': name, 'description': desc, 'deadline': deadline, 'priority': priority,"sub_task_id": 0,"status": 0,"type": type}
    else:
        reward_time = int(input('Enter the time it takes to complete the task in minutes: '))
        task = {'name': name, 'description': desc, 'deadline': deadline, 'priority': priority,"status": 0,"type": type,'reward_time': reward_time}
    df = pd.read_csv('tasks.csv',index_col=0)
    new_df = pd.DataFrame([task],index=[0])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv('tasks.csv')
    update_tasks()

def edit_task():
    print('Editing a task')
    df = pd.read_csv('tasks.csv',index_col=0)
    df = df[df['status'] != 3]
    print(tabulate(df[['name','status','deadline']],headers='keys',tablefmt='grid'))
    df = pd.read_csv('tasks.csv',index_col=0)
    task_index = input('Enter the index of the task you would like to edit: ')
    task = df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','description','status','deadline','type']],headers='keys',tablefmt='grid'))
    print('What task information would you like to change?')
    print('1. Name')
    print('2. Description')
    print('3. Deadline')
    print('4. Type')
    print('5. Cancel')
    change = input('Number: ')
    if change == '1':
        name = ui_entries.get_name()
        df.loc[int(task_index), 'name'] = name
    elif change == '2':
        desc = ui_entries.get_desc()
        df.loc[int(task_index), 'description'] = desc
    elif change == '3':
        deadline = ui_entries.get_deadline()
        df.loc[int(task_index), 'deadline'] = deadline
    elif change == '4':
        type, priority = ui_entries.get_type()
        df.loc[int(task_index), 'type'] = type
        df.loc[int(task_index), 'priority'] = priority
    elif change == '5':
        return
    else:
        print('Invalid input')
        edit_task()
        return
    df.to_csv('tasks.csv')

def start_task():
    print('Starting a task')
    df = pd.read_csv('tasks.csv',index_col=0)
    print(tabulate(df[df['status'] == 0][['name','type','deadline']].sort_values('deadline',ascending=True),headers='keys',tablefmt='grid'))
    task_index = input('Enter the index of the task you would like to start: ')
    task = df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    df.loc[int(task_index), 'status'] = 1                                                                                                                    
    df.loc[int(task_index), 'start_time'] = datetime.now()
    if df.loc[int(task_index), 'type'] == 'game':
        df.to_csv('tasks.csv')
        reward_view(task_index)
        df.loc[int(task_index), 'status'] = 3
    df.to_csv('tasks.csv')
    update_tasks()

def complete_task():
    print('Completing a task')
    df = pd.read_csv('tasks.csv',index_col=0)
    print(tabulate(df[df['status'] != 3][['name','type','deadline']].sort_values('deadline',ascending=True),headers='keys',tablefmt='grid'))
    task_index = input('Enter the index of the task you would like to complete: ')
    task = df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    df.loc[int(task_index), 'status'] = 3
    # df.loc[int(task_index), 'end_time'] = datetime.now()
    df.to_csv('tasks.csv')
    update_tasks()

def view_tasks():
    update_tasks()
    df = pd.read_csv('tasks.csv',index_col=0)
    df['deadline'] = pd.to_datetime(df['deadline'])
    df['wait_time'] = pd.to_datetime(df['wait_time'])
    print('Tasks')
    df = df[df['status'] != 3]
    df = df.sort_values(by=['priority','deadline'],ascending=True)
    for index, row in df.iterrows():
        if str(row['wait_time']) != 'NaT':
            if timedelta(hours=1) > row['wait_time'] - datetime.now():
                df.loc[index,'wait_time_remaining'] =  Fore.RED + str(row['wait_time'] - datetime.now()) + Fore.RESET
            elif timedelta(days=1) > row['wait_time'] - datetime.now():
                df.loc[index,'wait_time_remaining'] =  Fore.YELLOW + str(row['wait_time'] - datetime.now()) + Fore.RESET
            else:
                df.loc[index,'wait_time_remaining'] =  Fore.GREEN + str(row['wait_time'] - datetime.now()) + Fore.RESET
        if timedelta(hours=1) > row['deadline'] - datetime.now():
            df.loc[index,'time_remaining'] =  Fore.RED + str(row['deadline'] - datetime.now()) + Fore.RESET
        elif timedelta(days=1) > row['deadline'] - datetime.now():
            df.loc[index,'time_remaining'] =  Fore.YELLOW + str(row['deadline'] - datetime.now()) + Fore.RESET
        else:
            df.loc[index,'time_remaining'] =  Fore.GREEN + str(row['deadline'] - datetime.now()) + Fore.RESET
        if row['status'] == 0:
            df.loc[index,'status_show'] = Fore.GREEN + 'Not Started' + Fore.RESET
        elif row['status'] == 1:
            df.loc[index,'status_show'] = Fore.GREEN + 'In Progress' + Fore.RESET
        elif row['status'] == 2:
            df.loc[index,'status_show'] = Fore.YELLOW + 'Pended' + Fore.RESET
        if row['sub_task_id'] == 0:
            df.loc[index,'sub_task_cnt_left'] = Fore.WHITE + "0" + Fore.RESET
        else:
            sub_df = pd.read_csv('subtasks.csv',index_col=0)
            sub_df = sub_df[sub_df['id'] == row['sub_task_id']]
            df.loc[index,'sub_task_cnt_left'] = Fore.GREEN + str(len(sub_df[sub_df['status'] == 0])) + Fore.RESET

    print(tabulate(df[['name','status_show','sub_task_cnt_left','wait_time_remaining','time_remaining']],headers='keys',tablefmt='grid'))

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def pend_task():
    print('Pend a task')
    df = pd.read_csv('tasks.csv',index_col=0)
    print(tabulate(df[df['status'] == 1][['name','type','deadline']].sort_values('deadline',ascending=True),headers='keys',tablefmt='grid'))
    df['deadline'] = pd.to_datetime(df['deadline'])
    task_index = input('Enter the index of the task you would like to pend: ')
    time_pend = input('Enter the number of minutes, hours, days you would like to pend the task for: ex(30m, 1h, 2d): ')
    if df.loc[int(task_index),'deadline'] < datetime.now():
        df.loc[int(task_index),'deadline'] = datetime.now()+timedelta(hours=1)
        return
    
    if time_pend[-1] == 'm':
        df.loc[int(task_index),'deadline'] += pd.Timedelta(minutes=int(time_pend[:-1]))
        df.loc[int(task_index),'wait_time'] = datetime.now()+pd.Timedelta(minutes=int(time_pend[:-1]))
    elif time_pend[-1] == 'h':
        df.loc[int(task_index),'deadline'] += pd.Timedelta(hours=int(time_pend[:-1]))
        df.loc[int(task_index),'wait_time'] = datetime.now()+pd.Timedelta(hours=int(time_pend[:-1]))
    elif time_pend[-1] == 'd':
        df.loc[int(task_index),'deadline'] += pd.Timedelta(days=int(time_pend[:-1]))
        df.loc[int(task_index),'wait_time'] = datetime.now()+pd.Timedelta(days=int(time_pend[:-1]))
    df.loc[int(task_index),'status'] = 2
    df.to_csv('tasks.csv')
def create_subtask(index):
    print('Adding a subtask')
    df = pd.read_csv('tasks.csv',index_col=0)
    task = df.iloc[[index]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','status','deadline']],headers='keys',tablefmt='grid'))
    task = df.iloc[index]
    new_id = 0
    if task['sub_task_id'] == 0:
        new_id = df['sub_task_id'].max()+ 1
        df.loc[index, 'sub_task_id'] = new_id
    df.to_csv('tasks.csv')
    subtask_name = input('Enter the name of the subtask: ')
    subtask_desc = input('Enter the description of the subtask: ')
    status = 0
    sub_df = pd.read_csv('subtasks.csv',index_col=0)
    id_lst = list(sub_df[sub_df['id'] == task['sub_task_id']]["id"])
    if new_id == 0:
        new_id = id_lst[0]
    order = len(sub_df[sub_df['id'] == task['sub_task_id']])
    subtask = {'name': subtask_name, 'description': subtask_desc, 'status': status,"id": new_id,"order": order}
    new_sub_df = pd.DataFrame([subtask],index=[0])
    sub_df = pd.concat([sub_df, new_sub_df], ignore_index=True)
    sub_df.to_csv('subtasks.csv')
def edit_subtasks(index):
    print("Edit a substasks") 
    df = pd.read_csv('tasks.csv',index_col=0)
    task = df.iloc[[index]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','status','deadline']],headers='keys',tablefmt='grid'))
    task = df.iloc[index]
    id = task['sub_task_id']
    if id == 0:
        return
    sub_df = pd.read_csv("subtasks.csv",index_col=0)
    print(tabulate(sub_df[sub_df["id"]==id].sort_values("order",ascending = True)[['name','status','deadline']],headers='keys',tablefmt='grid'))
    task_index = input('Enter the index of the task you would like to edit: ')
    task = sub_df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','description','status','deadline','type']],headers='keys',tablefmt='grid'))
    print('What task information would you like to change?')
    print('1. Name')
    print('2. Description')
    change = input('Number: ')
    if change == '1':
        name = ui_entries.get_name()
        df.loc[int(task_index), 'name'] = name
    elif change == '2':
        desc = ui_entries.get_desc()
        df.loc[int(task_index), 'description'] = desc
    else:
        print('Invalid input')
        edit_task()
        return
    df.to_csv('tasks.csv')

def view_subtasks():
    print('View a subtasks')
    df = pd.read_csv('tasks.csv',index_col=0)
    print(tabulate(df[df['status']==0][['name','status','deadline']],headers='keys',tablefmt='grid'))
    task_index = input('Enter the index of the task you would like to view the subtasks of: ')
    task = df.iloc[[int(task_index)]]
    if task.empty:
        print('Task not found')
        return
    print(tabulate(task[['name','status','deadline']],headers='keys',tablefmt='grid'))
    task = df.iloc[int(task_index)]
    sub_df = pd.read_csv('subtasks.csv',index_col=0)
    sub_df = sub_df[sub_df['id'] == task['sub_task_id']]
    print(tabulate(sub_df[['name','status']],headers='keys',tablefmt='grid'))
    print("1. Create a task")
    print("2. Edit a task")
    print("3. Delete a task")
    choice = int(input("Action: "))
    if choice == 1:
        create_subtask(int(task_index))
    elif choice == 2:
        edit_subtasks(int(task_index))
    elif choice == 3:
        delete_subtasks(int(task_index))
    elif choice == 4:
        start_subtasks(int(task_index))
    elif choice == 5:
        complete_subtasks(int(task_index))
    else:
        print("Invalid Choice")


def reward_view(index):
    df = pd.read_csv('tasks.csv',index_col=[0])
    task = df.iloc[[int(index)]]
    print(tabulate(task[['name','status','deadline']],headers='keys',tablefmt='grid'))
    task = df.iloc[int(index)]
    if task.empty or task['type'] != 'game' or task['status'] != 1:
        print('Task Invalid')
        input('Press enter to continue')
        return
    reward_time = df.iloc[int(index)]['reward_time'] *60
    timer = time.time()+reward_time
    while time.time() < timer:
        print('\rTime remaining: ',timer-time.time(),end='')
        time.sleep(1)
    print('\nTime Ended!')
    input('Press enter to continue')


if __name__ == '__main__':
    # print(Fore.RED + 'This is red text'+ Fore.RESET)
    # breakpoint()
    # complete create a quick entry for adding the deadline
    # complete make task type a dropdown with number values
    # complete compress code
    # complete allow entry with just date or an hour
    # complete allow to skip reason for task creation due entry skip setting it to N/A
    # complete view tasks will default to filter by priority then by deadline
    # complete days remainning should be displayed in view tasks
    # complete start tasks should only show tasks that are not started
    # complete view tasks re index the values based status
    # complete add a delete task feature
    # complete reward task when category is set to Game 
    # complete add a live datetime timer
    # complete ability to pend tasks that I need to wait before starting again;
    # complete Color code status 0,1 are green, 2 is yellow, 
    # complete color code the tasks based on time left red is less than an hour, yellow is less than a day, green is more than a day
    # complete create a better view for the tasks
    # complete if a task is large enough, it should be broken down into subtasks which will be be replace by description
    # TODO add buttons for the actions
    # TODO each column priority, deadline should have a weight then be sorted based on that weight
    # TODO add repeatable tasks that'll auto add either everyday, every week, every month, every year
    # TODO habit creator
    # TODO when I make a change their should be a quick view of the change
    # TODO rewards for completing tasks
    # TODO add a time boxing feature for certain tasks that dont requre waiting and if the task is not completed then it push the other tasks back



    while True:
        clear_console()
        view_tasks()
        print("Task Manager")
        print("1. Create a task")
        print("2. Edit a task")
        print("3. Delete a task")
        print("4. Start a task")
        print("5. Pend a task")
        print("6. Complete a task")
        print("7. Create a subtask")
        print("8. View subtasks")
        print("Enter 'q' to quit")
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(60)
        while True:
            try:
                choice = input("Action: ")
                signal.alarm(0)
            except Exception:
                choice = 'r'
                break
            if choice == '1':
                clear_console()
                create_task()
                break
            elif choice == '2':
                clear_console()
                edit_task()
                break
            elif choice == '3':
                delete_task()
                edit_task()
                break
            elif choice == '4':
                clear_console()
                start_task()
                break
            elif choice == '5':
                clear_console()
                pend_task()
                break
            elif choice == '6':
                clear_console()
                complete_task()
                break
            elif choice == '7':
                clear_console()
                add_subtask()
                break
            elif choice == '8':
                clear_console()
                view_subtasks()
                break
            elif choice == 'q':
                clear_console()
                break
            else:
                print('Invalid input')
        if choice == 'q':
            break