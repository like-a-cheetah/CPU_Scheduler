"""
        작성자 : 컴퓨터소프트웨어공학과 20184009 김주원
        작성일 : 20.05.10 ~ 20.06.11
        프로그램명 : CPU Scheduler Simulator
        프로그램 설명 : 프로세스를 입력하여 생상하고 생성된 프로세스를 
                       스케줄러 알고리즘인 FCFS, SJF, 비선점 Priority,
                       선점 Priority, RR, SRT, HRN들의 각각의 실행 결과인
                       간트차트와 대기시간 응답시간, 반환시간을 GUI형태로
                       결과를 보여주는 프로그램

"""
import sys
from copy import copy, deepcopy
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas #그래프 모듈

class Process:      #프로세스 객체
    def __init__(self, PID, Arrive_T, Service_T, Priority): #프로세스 생성자
        self.PID = PID
        self.Arrive_T = Arrive_T
        self.Service_T = Service_T
        self.Priority = Priority

class Result(QDialog):  #두번째 윈도우 클래스
    def __init__(self, process, T_slice, Process_num):
        super().__init__()
        self.ui = uic.loadUi("Result_window.ui", self)
        self.ui.setWindowTitle("Result")
        
        self.T_slice = T_slice
        self.process = deepcopy(process)    #가져온 프로세스 깊은 복사
        self.P_num = Process_num
        
        self.set_Table()    #각 알고리즘의 결과 테이블 생성
        
        self.FCFS()
        self.SJF()
        self.HRN()
        self.None_Priority()
        self.RR()
        self.SRT()
        self.Priority()
            
        self.show()
        
    def FCFS(self):     
        ax = self.init(self.FCFS_C)     #그래프 생성
        ax.invert_yaxis()   
        
        PCB = self.init_P()     #프로세스에 필요한 초기화 호출
        PCB.sort(key=lambda x: (x.Arrive_T, x.PID))     #도착순, 이름순으로 정렬
            
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)  #실행중인 시간의 값 변수

        Wait_S = 0
        Resp_S = 0
        Return_S = 0    #각 시간값 총합
            
        for i in range(self.P_num): #FCFS알고리즘 동작
            if PCB[i].Arrive_T > Exec_T:    #다음 프로세스까지의 빈 간격 건너뛰기
                Exec_T = PCB[i].Arrive_T
            
            PCB[i].Wait_T = Exec_T - PCB[i].Arrive_T    #대기시간 계산
            Wait_S += PCB[i].Wait_T
            
            PCB[i].Resp_T = Exec_T - PCB[i].Arrive_T    #응답시간 계산
            Resp_S += PCB[i].Resp_T
            
            ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = PCB[i].Service_T, color = 'gray') #그래프에 그림
            
            Exec_T += PCB[i].Service_T    #진행된 시간 계산
            
            PCB[i].Return_T = Exec_T - PCB[i].Arrive_T  #반환시간 계산
            Return_S += PCB[i].Return_T
            
            self.one_row(self.FCFS_r, i, PCB[i])    #프로세스 결과값 출력
            
        ax.set_xticks(range(Exec_T + 1))    #그래프 눈금 할당
        self.ave_val(self.FCFS_r, Wait_S, Resp_S, Return_S)     #평균값 계산, 출력
            
    def SJF(self):
        ax = self.init(self.SJF_C)    #그래프 생성
        ax.invert_yaxis()
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0     
        
        PCB = self.init_P()     #프로세스에 필요한 초기화 호출
        PCB.sort(key=lambda x: (x.Arrive_T, x.Service_T, x.PID))    #도착순, 서비스시간순 정렬
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)  #첫 프로세스 도착 대기까지 빈 시간 그래프
            
        for i in range(self.P_num):
            if PCB[i].Arrive_T > Exec_T:
                Exec_T = PCB[i].Arrive_T
            
            PCB[i].Wait_T = Exec_T - PCB[i].Arrive_T
            Wait_S += PCB[i].Wait_T
            
            PCB[i].Resp_T = Exec_T - PCB[i].Arrive_T
            Resp_S += PCB[i].Resp_T
            
            ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = PCB[i].Service_T, color = 'gray')
            
            Exec_T += PCB[i].Service_T
            
            PCB[i].Return_T = Exec_T - PCB[i].Arrive_T
            Return_S += PCB[i].Return_T
            
            self.one_row(self.SJF_r, i, PCB[i])
            
            arrive = i + 1
            while arrive < self.P_num and PCB[arrive].Arrive_T <= Exec_T: 
                arrive += 1      #프로세스 실행동안 도착한 마지막 프로세스의 인덱스값 arrive
                
            if arrive <= self.P_num:
                PCB = copy(self.SJF_sort(PCB, i+1, arrive))  #도착한 프로세스들 서비스 시간 순으로 정렬
        
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.SJF_r, Wait_S, Resp_S, Return_S)
        
    def HRN(self):
        ax = self.init(self.HRN_C)
        ax.invert_yaxis()
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0 
        
        PCB = self.init_P()
        PCB.sort(key=lambda x: (x.Arrive_T, x.Service_T, x.PID))    #도착순 서비스시간 순 이름 순으로 정렬
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)  #첫프로세스 대기 그래프
            
        for i in range(self.P_num):
            if PCB[i].Arrive_T > Exec_T:
                Exec_T = PCB[i].Arrive_T
            
            PCB[i].Wait_T = Exec_T - PCB[i].Arrive_T
            Wait_S += PCB[i].Wait_T
            
            PCB[i].Resp_T = Exec_T - PCB[i].Arrive_T
            Resp_S += PCB[i].Resp_T
            
            ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = PCB[i].Service_T, color = 'gray')
            
            Exec_T += PCB[i].Service_T
            
            PCB[i].Return_T = Exec_T - PCB[i].Arrive_T
            Return_S += PCB[i].Return_T
            
            self.one_row(self.HRN_r, i, PCB[i])
            
            arrive = i + 1
            while arrive < self.P_num and PCB[arrive].Arrive_T <= Exec_T:     #도착한 프로세스를 알아냄
                Wait_T = Exec_T - PCB[arrive].Arrive_T   #도착한 프로세스 대기시간 계산
                PCB[arrive].Priority = self.HRN_P(Wait_T, PCB[arrive].Service_T) #우선순위 계산
                arrive += 1
                
            if i + 1 < self.P_num and PCB[i + 1].Arrive_T <= Exec_T:
                PCB = self.Descending_Psort(PCB, i+1, arrive)    #도착한 프로세스들 우선순위 내림차순으로 정렬
            
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.HRN_r, Wait_S, Resp_S, Return_S)
        
    def None_Priority(self):
        ax = self.init(self.NP_C)
        ax.invert_yaxis()
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0 
        
        PCB = self.init_P()
        PCB.sort(key=lambda x: (x.Arrive_T, x.Priority, x.PID))
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)
        
        for i in range(self.P_num):
            if PCB[i].Arrive_T > Exec_T:
                Exec_T = PCB[i].Arrive_T
            
            PCB[i].Wait_T = Exec_T - PCB[i].Arrive_T
            Wait_S += PCB[i].Wait_T
            
            PCB[i].Resp_T = Exec_T - PCB[i].Arrive_T
            Resp_S += PCB[i].Resp_T
            
            ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = PCB[i].Service_T, color = 'gray')
            Exec_T += PCB[i].Service_T
            
            PCB[i].Return_T = Exec_T - PCB[i].Arrive_T
            Return_S += PCB[i].Return_T
            
            self.one_row(self.NP_r, i, PCB[i])
            
            arrive = i + 1
            while arrive < self.P_num and PCB[arrive].Arrive_T <= Exec_T:
                arrive += 1      
            if i + 1 < self.P_num and PCB[i + 1].Arrive_T <= Exec_T:
                PCB = self.Ascending_Psort(PCB, i+1, arrive)  #우선순위 오름차순 정렬
                
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.NP_r, Wait_S, Resp_S, Return_S)
       
    def RR(self):
        ax = self.init(self.RR_C)
        ax.invert_yaxis()
        
        process = self.init_P()
        process.sort(key=lambda x: x.Arrive_T)
        
        PCB = []
        PCB.append(process[0])  #대기 큐에 첫 프로세스 도착
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)
        
        total_T = 0
        for i in range(self.P_num):
            total_T += process[i].Service_T 
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0 
        
        used = 1
        row = 0
        
        pre = 0
        while total_T:      #실행될 총 시간이 끝날때까지 반복
            if PCB[pre].Arrive_T > Exec_T:
                Exec_T = PCB[pre].Arrive_T
                
            if PCB[pre].First:
                PCB[pre].Resp_T = Exec_T - PCB[pre].Arrive_T    #CPU에 처음 올라온 프로세스 응답시간 계산
                PCB[pre].Wait_T += Exec_T - PCB[pre].Arrive_T   #첫 대기시간 계산
                PCB[pre].First = False    #처음이 False(아니다)
                
            elif not PCB[pre].First:  #처음이 아니므로 전에 타임아웃 된 시간으로 대기시간 계산
                PCB[pre].Wait_T += Exec_T - PCB[pre].Stop_T
            
            if PCB[pre].Service_T <= self.T_slice:    #남은 서비스시간이 타임슬라이스보다 작다면 
                ax.barh('p'+str(PCB[pre].PID), left = Exec_T, width = PCB[pre].Service_T, color = 'gray') #남은 시간으로 그래프 그림
                Exec_T += PCB[pre].Service_T
                total_T -= PCB[pre].Service_T     #남은 시간으로 실행시간 누적, 남은 실행시간 차감
                PCB[pre].Service_T = 0    #프로세스의 남은 서비스시간 0
                PCB[pre].Return_T = Exec_T - PCB[pre].Arrive_T 
            else:       #서비스시간이 타임슬라이스보다 크다면
                ax.barh('p'+str(PCB[pre].PID), left = Exec_T, width = self.T_slice, color = 'gray')
                Exec_T += self.T_slice
                total_T -= self.T_slice     #타임 슬라이스로 실행시간 누적, 남은 실행시간 차감
                PCB[pre].Stop_T = Exec_T      #타임아웃 된 시간
                PCB[pre].Service_T -= self.T_slice    #프로세스의 남은 서비스시간 - 타임 슬라이스
            
            while used < self.P_num and process[used].Arrive_T <= Exec_T:
                PCB.append(process[used])   #도착한 프로세스 대기 큐에 삽입
                used += 1   #사용된 프로세스 개수(사용될 프로세스 인덱스)    
            
            if not PCB[pre].Service_T:    #서비스 시간이 끝남
                self.one_row(self.RR_r, row, PCB[pre])    #실행 결과 출력
                
                Wait_S += PCB[pre].Wait_T
                Resp_S += PCB[pre].Resp_T
                Return_S += PCB[pre].Return_T
                
                del PCB[pre]  #해당 프로세스 삭제
                
                row += 1
                
            elif len(PCB) > 1 and PCB[pre].Service_T:  #남아 있다면 문맥교환
                PCB.append(PCB[pre])    #가장 뒤로 이동
                del PCB[pre]
                
            if used < self.P_num and not len(PCB):  
                PCB.append(process[used])   #대기큐가 비었다면, 실행된 시간보다 도착시간이 늦는 프로세스를 가져옴 
                used += 1
                
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.RR_r, Wait_S, Resp_S, Return_S)
            
    def SRT(self):
        ax = self.init(self.SRT_C)
        ax.invert_yaxis()
        
        process = self.init_P()
        process.sort(key=lambda x: (x.Arrive_T, x.Service_T))
        
        PCB = []
        PCB.append(process[0])
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)
        
        total_T = 0
        for i in range(self.P_num):
            total_T += process[i].Service_T 
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0 
        
        used = 1
        row = 0
        
        i = 0
        while total_T:
            if PCB[i].Arrive_T > Exec_T:
                Exec_T = PCB[i].Arrive_T
                
            if PCB[i].First:
                PCB[i].Resp_T = Exec_T - PCB[i].Arrive_T
                PCB[i].Wait_T += Exec_T - PCB[i].Arrive_T
                PCB[i].First = False
                
            elif not PCB[i].First:
                PCB[i].Wait_T += Exec_T - PCB[i].Stop_T
            
            if PCB[i].Service_T <= self.T_slice:    #타임슬라이스보다 남은 서비스시간이 작을 경우 남은 시간으로 실행
                ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = PCB[i].Service_T, color = 'gray')
                Exec_T += PCB[i].Service_T
                total_T -= PCB[i].Service_T
                PCB[i].Service_T = 0
                PCB[i].Return_T = Exec_T - PCB[i].Arrive_T 
            else:   #남은 서비스시간이 타임슬라이스보다 크면 타임슬라이스 사용
                ax.barh('p'+str(PCB[i].PID), left = Exec_T, width = self.T_slice, color = 'gray')
                Exec_T += self.T_slice
                total_T -= self.T_slice
                PCB[i].Stop_T = Exec_T
                PCB[i].Service_T -= self.T_slice
                   
            if not PCB[i].Service_T:    #서비스 시간이 끝난 경우 해당 프로세스 제거
                self.one_row(self.SRT_r, row, PCB[i])
                
                Wait_S += PCB[i].Wait_T
                Resp_S += PCB[i].Resp_T
                Return_S += PCB[i].Return_T
                
                del PCB[i]  #프로세스 반환
                
                row += 1
            
            while used < self.P_num and process[used].Arrive_T <= Exec_T:
                PCB.append(process[used])   #도착한 프로세스 삽입
                used += 1
                    
            if used < self.P_num and not len(PCB):  #늦게 도착하는 프로세스 가져옴
                PCB.append(process[used])
                used += 1
                
            PCB.sort(key=lambda x: (x.Service_T))   #남은 서비스 시간으로 정렬
                
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.SRT_r, Wait_S, Resp_S, Return_S)
       
    def Priority(self):     
        ax = self.init(self.P_C)
        ax.invert_yaxis()
        
       
        process = self.init_P()
        process.sort(key=lambda x: (x.Arrive_T, x.Priority))
        
        PCB = []
        PCB.append(process[0])
        
        Exec_T = self.empty_T(ax, PCB[0].Arrive_T)
        
        total_T = 0
        for i in range(self.P_num):
            total_T += process[i].Service_T 
        
        Wait_S = 0
        Resp_S = 0
        Return_S = 0 
        
        used = 1
        row = 0
        
        pre = 0
        while total_T:
            change = False
            if PCB[pre].Arrive_T > Exec_T:
                Exec_T = PCB[pre].Arrive_T
                
            if PCB[pre].First:
                PCB[pre].Wait_T += Exec_T - PCB[pre].Arrive_T
                PCB[pre].Resp_T = Exec_T - PCB[pre].Arrive_T
                PCB[pre].First = False
                
            elif PCB[pre].Stop_T:
                PCB[pre].Wait_T += Exec_T - PCB[pre].Stop_T
            
            while not change and PCB[pre].Service_T:   #서비스 시간이 남았고, 문맥교환 불필요시에 반복
                ax.barh('p'+str(PCB[pre].PID), left = Exec_T, width = 1, color = 'gray')
                
                PCB[pre].Service_T -= 1     #서비스 시간 1초 진행
                Exec_T += 1
                total_T -= 1
                
                while used < self.P_num and process[used].Arrive_T == Exec_T: 
                    PCB.append(process[used])   #1초가 지났을때 도착한 프로세스 추가
                    if PCB[pre].Service_T and process[used].Priority < PCB[pre].Priority:
                        PCB[pre].Stop_T = Exec_T    #새로운 PCB가 실행중인 PCB보다 우선순위가 큰(숫자가 작은)경우 문맥교환 발생
                        change = True   #문맥교환의 필요를 표시
                    used += 1
                
            if not PCB[pre].Service_T:    #프로세스 반환, 결과 출력
                PCB[pre].Return_T = Exec_T - PCB[pre].Arrive_T
                
                self.one_row(self.P_r, row, PCB[pre])
                
                Wait_S += PCB[pre].Wait_T
                Resp_S += PCB[pre].Resp_T
                Return_S += PCB[pre].Return_T 
                
                del PCB[pre]
                
                row += 1
                
                if used < self.P_num and not len(PCB):   #늦게 도착하는 프로세스 가져옴
                    PCB.append(process[used])
                    used += 1                
                    
            PCB.sort(key=lambda x: (x.Priority, x.Arrive_T))    #우선순위 오름차순 정렬
            
        ax.set_xticks(range(Exec_T + 1))
        self.ave_val(self.P_r, Wait_S, Resp_S, Return_S)
       
    def set_Table(self):    #각 알고리즘의 결과 테이블 생성
        self.FCFS_r.setRowCount(self.P_num + 1)
        self.FCFS_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.FCFS_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.SJF_r.setRowCount(self.P_num + 1)
        self.SJF_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.SJF_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.HRN_r.setRowCount(self.P_num + 1)
        self.HRN_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.HRN_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.NP_r.setRowCount(self.P_num + 1)
        self.NP_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.NP_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.RR_r.setRowCount(self.P_num + 1)
        self.RR_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.RR_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.SRT_r.setRowCount(self.P_num + 1)
        self.SRT_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.SRT_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
        self.P_r.setRowCount(self.P_num + 1)
        self.P_r.setVerticalHeaderItem(self.P_num, QTableWidgetItem('평균'))
        self.P_r.setItem(self.P_num, 0, QTableWidgetItem('-'))
        
    def init(self, algo_C): #그래프 캔버스 생성
        canvas = FigureCanvas()
        algo_C.addWidget(canvas)
        ax = canvas.figure.subplots()
        return ax
        
    def init_P(self):   #프로세스 리스트 복사, 초기화
        process = deepcopy(self.process)
        for i in range(self.P_num):
            process[i].First = True
            process[i].Wait_T = 0
            process[i].Stop_T = 0
            process[i].Resp_T = 0
            process[i].Return_T = 0
        return process
    
    def empty_T(self, ax, empty_T): #프로세스 도착 전, 빈 시간 그래프
        if empty_T:
            print("432")
            ax.barh(str('Empty'), left = 0, width = empty_T, color = 'w')
        return empty_T
    
    def SJF_sort(self, orignal, first, last):   #리스트 일정 범위 서비스 시간 기준 오름차순 정렬
        new_list = orignal[first:last]
        new_list.sort(key=lambda x: (x.Service_T, x.Arrive_T, x.PID))
        orignal[first:last] = new_list
        return orignal
    
    def HRN_P(self, wait_T, serv_T):    #우선순위 계산
        return (wait_T + serv_T)/serv_T
    
    def Descending_Psort(self, orignal, first, last):   #리스트 일정 범위 우선순위로 내림차순 정렬
        new_list = orignal[first:last]
        new_list.sort(key=lambda x: (-x.Priority))
        orignal[first:last] = new_list
        return orignal
    
    def Ascending_Psort(self, orignal, first, last):    #리스트 일정 범위 우선순위로 오름차순 정렬
        new_list = orignal[first:last]
        new_list.sort(key=lambda x: (x.Priority))
        orignal[first:last] = new_list
        return orignal
    
    def one_row(self, Table, row, PCB):
        Table.setItem(row, 0, QTableWidgetItem('p'+str(PCB.PID)))     #PID
        Table.setItem(row, 1, QTableWidgetItem(str(PCB.Wait_T)))   #대기시간
        Table.setItem(row, 2, QTableWidgetItem(str(PCB.Resp_T)))
        Table.setItem(row, 3, QTableWidgetItem(str(PCB.Return_T)))   #반환시간
        
    def ave_val(self, Table, Wait, Resp, Return):
        Table.setItem(self.P_num, 1, QTableWidgetItem(str(round(Wait / self.P_num, 3)))) #평균 대기시간
        Table.setItem(self.P_num, 2, QTableWidgetItem(str(round(Resp / self.P_num, 3)))) #평균 응답시간
        Table.setItem(self.P_num, 3, QTableWidgetItem(str(round(Return / self.P_num, 3)))) #평균 반환시간 
        
class Simulator(QDialog):   #첫 번째 윈도우 클래스
    def __init__(self):     #화면 객체 생성자
        super().__init__()
        self.ui = uic.loadUi("CPU_Scheduler.ui", self)
        self.ui.setWindowTitle("CPU Scheduler")
        self.Btn_Assign.clicked.connect(self.Assign_event)       #할당 버튼 커맨드 연결
        self.Btn_Creation.clicked.connect(self.Creation_event)   #생성 버튼 커맨드 연결
        self.Btn_Execution.clicked.connect(self.Execution_event) #실행 버튼 커맨드 연결
        self.show()
        self.process=list()
        
    def Assign_event(self):     #할당 버튼 커맨드 함수
        self.Process_num = int(self.Process_n.text())    #입력값 프로세스값 변수에 정수형 저장
        self.Process_Table.setRowCount(self.Process_num) #저장된 값 만큼 행 생성
        
    def Creation_event(self):   #실행 버튼 커맨드 함수
        self.Time_slice = int(self.T_slice.text())      #입력값 타임슬라이스 변수에 정수형 저장
        for row in range(self.Process_num):     #프로세스 개수만큼 행에 입력된 값 반복하여 읽어옴
            PID = (int(self.Process_Table.item(row, 0).text()))
            Arrive_T = (int(self.Process_Table.item(row, 1).text()))
            Service_T = (int(self.Process_Table.item(row, 2).text()))
            Priority = (float(self.Process_Table.item(row, 3).text()))
            self.process.append(Process(PID, Arrive_T, Service_T, Priority))    #읽어온 값으로 프로세스 생성
        
    def Execution_event(self):  #실행 버튼 커맨드 함수
        window2 = Result(self.process, self.Time_slice, self.Process_num) #프로세스, 타임슬라이스값으로 두번째 윈도우 객체 생성
        window2.exec_()     #두번째 윈도우 실행
        

app = QApplication(sys.argv)
window = Simulator()    
window.show()   #첫번째 윈도우 출력
app.exec_()