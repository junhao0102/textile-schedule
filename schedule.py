import matplotlib.pyplot as plt
import streamlit as st
import math

def schedule(predict_data,mechine_data):
    #----準備排程資料----
    num_machines = len(mechine_data)
    order_number = predict_data["訂單編號"].tolist()
    duration = predict_data["織造時間(天)"].tolist()
    duration_hour = predict_data["織造時間(小時)"].tolist()
    deadline = predict_data["交期(天)"].tolist()
    length = predict_data["織造數量(米)"].tolist()
    flaw = predict_data["瑕疵數"].tolist()
    orders = [{"order_number":a,"length":b,"duration":c,"duration_hour":d,"deadline":e,"flaw":f} for a,b,c,d,e,f in zip(order_number,length,duration,duration_hour,deadline,flaw)]
    initial_waiting_time = mechine_data["幾日後可加入生產"].tolist()
    #----排程----
    orders.sort(key=lambda x: (x['deadline'], x['duration']))
    machine_assignments = [[] for _ in range(num_machines)]
    machine_end_times = [0] * num_machines
    next_available_times = initial_waiting_time[:]
    #----找出最早的可用機台----
    def find_earliest_machine():
        earliest_time = float('inf')
        earliest_machine = None
        for i in range(num_machines):
            available_time = max(machine_end_times[i], next_available_times[i])
            if available_time < earliest_time:
                earliest_time = available_time
                earliest_machine = i
        return earliest_machine, earliest_time
    #----找出已有訂單且最適合的機台----
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
                    # 最早可用的時間已超過截止日期，停止處理此訂單
                    break
                split_duration = min(remaining_duration, order['deadline'] - earliest_time)
                best_fit_machine = earliest_machine
                earliest_time = max(machine_end_times[best_fit_machine], next_available_times[best_fit_machine])
            else:
                # 找到合適的機台，計算開始和結束時間
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
        st.markdown('<font color="red" style="font-size: 24px;"><b>逾期訂單</b></font>', unsafe_allow_html=True)
        for order in late_orders:
            st.markdown(f'<li style="font-size: 24px;">{order}</li>', unsafe_allow_html=True)
    else:
        st.markdown('<font color="blue" style="font-size: 24px;">**所有訂單均已安排完成**</font>', unsafe_allow_html=True)
    return machine_assignments
            
#----繪製甘特圖----
def plot_gantt_chart(machine_assignments):
    #設置40種顏色
    colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf', '#1a9850', '#fdae61', '#6baed6', '#ff9e9e', '#ffdc9e', '#c7c7c7',
    '#6b6ecf', '#5ca487', '#9b9b7a', '#caab5e', '#ffcc99', '#ff6961', '#3c9f9a', '#aecaae',
    '#ff9896', '#9898ff', '#8fd6a1', '#c9d9cb', '#ffd700', '#7f9aa8', '#003366', '#ff6666',
    '#a3a3c2', '#b2df8a', '#ff8080', '#4682b4', '#9370db', '#ffc125', '#9f79ee', '#daa520'
]
    plt.figure(figsize=(12, 6))
    # 哈希表用於記錄每個訂單的顏色
    color_dict = {}
    for machine_index, assignments in enumerate(machine_assignments):
        for task in assignments:
            order_number = task['order_number']
            start_time = task['start_time']
            end_time = task['end_time']
            duration = end_time - start_time
             # 根據訂單號確定顏色
            color = color_dict.setdefault(order_number, colors[len(color_dict) % len(colors)])
            plt.barh(y=machine_index, width=duration, left=start_time, height=0.4, color=color, edgecolor='black')
            # 繪製開始和結束時間的垂直虛線
            # plt.axvline(x=start_time, color='gray', linestyle='--', linewidth=0.5)
            # plt.axvline(x=end_time, color='gray', linestyle='--', linewidth=0.5)

    patches = [plt.Rectangle((0,0),1,1, color=color_dict[order]) for order in color_dict]
    plt.legend(patches, color_dict.keys(), bbox_to_anchor=(1.05, 0.7), loc='upper left', borderaxespad=0.,fontsize="large")
    plt.yticks(range(len(machine_assignments)), [f'Machine {i+1}' for i in range(len(machine_assignments))])
    plt.xticks(range(math.ceil(max([task['end_time'] for assignments in machine_assignments for task in assignments]))+1))
    plt.tight_layout()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()







