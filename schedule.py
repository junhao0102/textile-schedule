import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import math

#----準備排程資料----
def schedule_info(predict_data,mechine_data):
    num_machines = len(mechine_data)
    order_number = predict_data["訂單編號"].tolist()
    duration = predict_data["織造時間(天)"].tolist()
    duration_hour = predict_data["織造時間(小時)"].tolist()
    deadline = predict_data["交期(天)"].tolist()
    length = predict_data["織造數量(米)"].tolist()
    flaw = predict_data["瑕疵數"].tolist()
    jobs = [{"order_number":a,"length":b,"duration":c,"duration_hour":d,"deadline":e,"flaw":f} for a,b,c,d,e,f in zip(order_number,length,duration,duration_hour,deadline,flaw)]
    machine_wait_times = mechine_data["幾日後可加入生產"].tolist()
    return jobs,num_machines,machine_wait_times

def schedule(orders, num_machines, initial_waiting_time):
    orders.sort(key=lambda x: (x['deadline'], x['duration']))
    machine_assignments = [[] for _ in range(num_machines)]
    machine_end_times = [0] * num_machines
    next_available_times = initial_waiting_time[:]

    def find_earliest_machine():
        earliest_time = float('inf')
        earliest_machine = None
        for i in range(num_machines):
            available_time = max(machine_end_times[i], next_available_times[i])
            if available_time < earliest_time:
                earliest_time = available_time
                earliest_machine = i
        return earliest_machine, earliest_time

    def find_best_fit_machine(order_duration, order_deadline):
        best_fit_machine = None
        best_fit_machine_time = float('inf')
        for i in range(num_machines):
            if machine_assignments[i]:
                available_time = max(machine_end_times[i], next_available_times[i])
                if available_time + order_duration <= order_deadline and available_time < best_fit_machine_time:
                    best_fit_machine = i
                    best_fit_machine_time = available_time
        return best_fit_machine
    
    late_orders = []
    for order in orders:
        remaining_duration = order['duration']
        order_split = False
        while remaining_duration > 0:
            best_fit_machine = find_best_fit_machine(remaining_duration, order['deadline'])
            if best_fit_machine is None:
                earliest_machine, earliest_time = find_earliest_machine()
                if earliest_time >= order['deadline']:
                    break
                split_duration = min(remaining_duration, order['deadline'] - earliest_time)
                best_fit_machine = earliest_machine
                earliest_time = max(machine_end_times[best_fit_machine], next_available_times[best_fit_machine])
            else:
                earliest_time = max(machine_end_times[best_fit_machine], next_available_times[best_fit_machine])
                split_duration = min(remaining_duration, order['deadline'] - earliest_time)

            end_time = earliest_time + split_duration
            machine_assignments[best_fit_machine].append({
                'order_number': order['order_number'],
                'start_time': earliest_time,
                'end_time': end_time,
                'duration_hour': format(order['duration_hour']/order['duration']*split_duration, '.2f'),
                'length': format(order['length']/order['duration']*split_duration, '.2f'),
                'flaw': format(order['flaw']/order['duration']*split_duration, '.2f')
            })
            machine_end_times[best_fit_machine] = end_time
            next_available_times[best_fit_machine] = end_time
            remaining_duration -= split_duration
            order_split = True
        
        if remaining_duration > 0 or not order_split:
            late_orders.append(order["order_number"])

    if late_orders:
        st.markdown('<font color="blue">**逾期訂單:**</font>', unsafe_allow_html=True)
        st.write(late_orders)
    else:
        st.markdown('<font color="blue">**所有訂單均已安排完成**</font>', unsafe_allow_html=True)
    plot_gantt_chart(machine_assignments)
    print(machine_assignments)
    print('='*30)
    return machine_assignments
            

#----繪製甘特圖----
def plot_gantt_chart(machine_assignments):
    colors = plt.cm.tab20.colors 
    plt.figure(figsize=(12, 6))
    # 哈希表用於記錄每個訂單的顏色
    color_dict = {}
    # 畫出每台機器的每個工單
    for machine_index, assignments in enumerate(machine_assignments):
        for task in assignments:
            order_number = task['order_number']
            start_time = task['start_time']
            end_time = task['end_time']
            duration = end_time - start_time
            color = color_dict.setdefault(order_number, colors[len(color_dict) % len(colors)])
            plt.barh(y=machine_index, width=duration, left=start_time, height=0.4, color=color, edgecolor='black')

            # 在订单的开始和结束处添加垂直虚线
            plt.axvline(x=start_time, color='gray', linestyle='--', linewidth=0.5)
            plt.axvline(x=end_time, color='gray', linestyle='--', linewidth=0.5)

    patches = [plt.Rectangle((0,0),1,1, color=color_dict[order]) for order in color_dict]
    plt.legend(patches, color_dict.keys(), bbox_to_anchor=(1.05, 0.7), loc='upper left', borderaxespad=0.,fontsize="large")
    plt.yticks(range(len(machine_assignments)), [f'Machine {i+1}' for i in range(len(machine_assignments))])
    plt.xticks(range(math.ceil(max([task['end_time'] for assignments in machine_assignments for task in assignments]))+1))
    plt.tight_layout()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()







