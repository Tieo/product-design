# -*- coding: utf-8 -*-
"""Mini_Poker1_4.2.1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aJiX4HP-gmu0fl02IlrPEYoCEeGs3D0E
"""

# -*- conding: utf-8 -*-
import numpy   as np
import random
import copy
import time
import csv

class Environment:
    #게임판 구성, 안되는 상태, 완료된 상태, 보상 정의
    #게임판 핸드만 두장 줌, 베팅 한 번씩 물어봄. 리레이즈 1회만 가능

    # 덱을 만듬. 턴, 판돈, 플레이어가 베팅한 횟수 설정

    def __init__(self):
        self.done = False #True면 게임 종료
        #self.winner = 0
        self.reward = 0
        self.turn = 0
        self.table = 0
        self.player_calls =0
        self.lowlimit = 200
        self.maxlimit = 2000
        self.bet1 = -2
        self.bet2 = -2
        self.last_bet = -2
        deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
        random.shuffle(deck)
        self.deck = deck

    # 보상을 정의  handcheck, ai_action은 agent가 준다.
    def pf_reward(self, handcheck, ai_action):
        #print('hc, a', handcheck, ai_action)
        if (handcheck == 1) and (ai_action > 0):
            # if ai_action >= 0:  # 콜, 레이즈, 체크
            rwd = -1
        elif (handcheck == 1) and (ai_action < 0):  # 폴드한 경우
            rwd = +1

        elif (handcheck != 1) and (ai_action > 0):
            # if ai_action >= 0:  # 콜, 레이즈, 체크
            rwd = +1
        else:  # 폴드한 경우
            rwd = -1

        return rwd

    def move(self, p1,p2):
        #각플레이어가 선택한 행동 table에 반영하고 게임 상태 판단
        #p1 = 1, p2 = -1
        #각 플레이어는 행동을 선택하는 메서드를 가짐 selct_action
        
        self.table += 400 # Blind 
        p1.bal -= 200
        p2.bal -= 200

        self.bet1 = p1.select_action(env) # 행동 선택 1
        self.last_bet = self.bet1
        if self.bet1 == -1: #폴드한 경우, 판돈에 돈을 넣지 않음
          pass
        else:
          self.table += self.bet1
        self.player_calls += 1 # p1 행동 카운트#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       
        self.bet2 = p2.select_action(env)#, player) # p2 행동 선택
        self.last_bet = self.bet2
        if self.bet2 == -1:
            pass
        else:
          self.table += self.bet2 # p2의 금액 추가 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.player_calls += 1 # p2 의 행동 카운트 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if (self.bet1>=0) and (self.bet2 > self.bet1): #리레이즈 
          self.bet1 = p1.select_action(env) # 한번 더 행동을 받음 # 행동선택 3 
          self.player_calls += 1 # 다시 p1 의 행동 카운트 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
          self.last_bet = self.bet1
          if self.bet1 == -1:
            pass
          else:
            self.table += self.bet1

        else:
          self.player_calls += 1 # 행동 3번으로 맞추기 용도#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.last_bet = -2 #원상복구
        #게임 상태가 종료인지 판단, 누가 이겼는지 체크
        #print('p calls', env.player_calls)
        self.end_check(p1,p2)
        self.player_calls =0
        return self.reward, self.done

    #현재 베팅 가능한 상태 수집.
    def get_action(self):
        observation = [-1,0]
        #table이 0이 아니다. -> 누군가 베팅을 했다면 lowlimit 이 그 두배로 바뀜

        if self.last_bet > 0:
          if self.last_bet*2 > 2000:
            self.lowlimit = 2000
          else:
            self.lowlimit =  self.last_bet*2
        #print('self.last_bet:{}, self.lowlimit:{}'.format(self.last_bet, self.lowlimit))
        for i in range(self.lowlimit, self.maxlimit+1,10): #이 부분 변경하면 경우의 수를 줄일 수 있음.
            observation.append(i)
        #print("in get action observation[] : ", observation)
        return observation

    #게임 종료 판단
    def end_check(self, p1,p2):
        if (self.player_calls >= 3): #

            #판돈에 플레이어의 베팅을 반영 및 표시
            if (self.bet1 == -1): #P1 폴드 
              p2.bal += self.table
              self.table = 0
              self.reward = -1 # 승자는 p2
              self.done = True
              
            elif (self.bet2 == -1): # P2 폴드
              p1.bal += self.table
              self.table = 0
              self.reward = 1 #승자는 p1
              self.done = True
              
            else: # 카드 점수 계산 
              # 1. p1 승리
              if self.hand_check(p1.hand1, p1.hand2) > self.hand_check(p2.hand1, p2.hand2):
                  self.reward = 1
                  p1.bal += self.table  # 테이블의 돈을 가져감
                  self.table = 0
                  self.done = True
              # 2. p2 승리
              elif self.hand_check(p1.hand1, p1.hand2) < self.hand_check(p2.hand1, p2.hand2):
                  self.reward = -1
                  p2.bal += self.table  # 테이블의 돈을 가져감
                  self.table = 0
                  self.done = True
              # 3. p1 p2카드가 같다. -> 무승부 판돈 분할
              else:
                  self.reward = 0
                  p1.bal += self.table/2
                  p2.bal += self.table/2
                  self.table = 0
                  self.done = True # 돈은 그대로 남아있음.
        else:
            pass
        return

    def print_poker(self, player):
        print('\n------------------Turn : %d-------------------\n'%self.turn)
        print('Table Money: %d'%self.table)
        print('Now Bet: %s'%player.name)

    # 핸드 순위 확인
    def hand_check(self, hand1, hand2):  # 핸드체크, 프레플랍 단계 먼저 자신에게 주어진 카드 정보를 분석한다.
        premium = [('p', 14, 14), ('p', 13, 13), ('p', 12, 12), ('s', 14, 13), ('p', 11, 11), ('s', 14, 12),
                   ('s', 13, 12), ('s', 14, 11), ('s', 13, 11), ('p', 10, 10), ('o', 14, 13), ('s', 14, 10),
                   ('s', 12, 11), ('s', 13, 10), ('s', 12, 10), ('s', 11, 10), ('p', 9, 9)]
        special = [('o', 14, 12), ('s', 14, 9), ('o', 13, 12), ('p', 8, 8), ('s', 13, 9), ('s', 10, 9),
                   ('s', 14, 8),
                   ('s', 12, 9), ('s', 11, 9), ('o', 14, 11), ('s', 14, 5), ('p', 7, 7), ('s', 14, 7),
                   ('o', 13, 11),
                   ('s', 14, 4), ('s', 14, 3), ('s', 14, 6)]
        good = [('o', 12, 11), ('p', 6, 6), ('s', 13, 8), ('s', 10, 8), ('s', 14, 2), ('s', 9, 8), ('s', 11, 8),
                ('o', 14, 10), ('s', 12, 8), ('s', 13, 7), ('o', 13, 10), ('p', 5, 5), ('o', 11, 10), ('s', 8, 7),
                ('o', 12, 10), ('p', 4, 4), ('p', 3, 3), ('p', 2, 2)]
        
        # 숫자 비교 후 pair인지 확인(pair이면 p, 아니면 문자 확인으로 넘어감), 문자 확인해서 일치하는지 확인(불일치 하면 o, 일치하면 s ),  숫자 조합해서 하나의 튜플로 제작
        if hand1[1] == hand2[1]:
            tup1 = 'p'
        else:
            if hand1[0] == hand2[0]:
                tup1 = 's'
            else:
                tup1 = 'o'

        if hand1[1] > hand2[1]:  # 숫자 큰 게 앞으로 오게 함
            tup2, tup3 = hand1[1], hand2[1]
        else:
            tup2, tup3 = hand2[1], hand1[1]

        tup = (tup1, tup2, tup3)  # 튜플 생성
        #print('tup', tup)
        if premium.count(tup) == 1:
            return 4  # ('premium')
        elif special.count(tup) == 1:
            return 3  # ('special')
        elif good.count(tup) == 1:  # 판단
            return 2  # ('good')
        else:
            return 1  # ('fold')

class Human_player:
    
    
    def __init__(self):
        self.name = 'Human Player'
        self.bal = 50000
        self.hand1 = 0
        self.hand2 = 0
    
    
    def select_action(self, env):#,player):
        while True:
            available_action = env.get_action()
            if (env.bet1 >= 0) and (env.bet2>= 2*env.bet1): #리레이즈의 상황이라면  0614 changed from here @@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              available_action = [-1, 0]#env.bet2] #폴드하거나 p2 bet 콜만 함 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              #env.maxlimit = env.bet2
              print('possible action: ', available_action)#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              print('{} Hands: {} {}'.format(self.name, self.hand1, self.hand2))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              print('player_calls',env.player_calls)#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              action = int(input('fold: -1 , call: 0\n'))#{}\n'.format(env.bet2)))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

            else:#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             print('possible action: ', available_action)#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             print('{} Hands: {} {}'.format(self.name, self.hand1, self.hand2))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             action = int(input('fold: -1, call: 0, {} <= raise <= {}\n'.format(env.lowlimit, env.maxlimit)))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # until here @@@@@@@@@@@@@@@@@@@@@@@@

            if action in available_action:
              if action == 0: # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
                if (env.player_calls == 0) and (env.last_bet==-2):
                  action = 0
                  
                elif env.player_calls == 1:
                  action = env.last_bet# p1이 제시한 금액에 p2가 콜하는 경우 
                else:
                  action = env.last_bet - env.bet1 #p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

              if action == -1:
                pass
              else:
                self.bal -= action
              break # 0614 break @@@@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            else:
                print("Wrong Action. Try Again")
        print('Human action: ', action)
        return action # 0614 action @@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

class Random_player:
    
    def __init__(self):
        self.name = 'Random Player'
        self.bal = 50000
        self.hand1 = 0
        self.hand2 = 0

    def select_action(self, env):
        
        available_action = env.get_action()
        #print(env.bet1)
        if (env.bet1 >= 0) and (env.bet2>= 2*env.bet1): #리레이즈의 상황이라면 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
          available_action = [-1, 0] #폴드, 콜만 함#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        action = random.choice(available_action) # 임의로 행동 선택

        #print('player_calls, available_action', env.player_calls, available_action)
        if action == 0: # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
          if (env.player_calls == 0) and (env.last_bet==-2):
            action = 0
          elif env.player_calls == 1:
            action = env.last_bet# p1이 제시한 금액에 p2가 콜하는 경우 
          else:
            action = env.last_bet - env.bet1 #p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if action == -1:
          pass
        else:
          self.bal -= action
        #print("rand P action : ", action)
        return action

class Monte_Carlo_player:
  def __init__(self):
    self.name = "MC Player"
    self.num_playout = 10 # 최대 약 1300  예상, 덱에서 2장 뽑는 경우의 수 고려.
    self.bal = 50000
    self.hand1 = 0
    self.hand2 = 0
    self.select_time1 = 0
    self.select_time2 = 0 
    self.bluff = ['y','y','y','y','y','n','n','n','n','n'] # 블러핑 확률 계산용, 잔고 앞자리 숫자에 맞게 'y'가 늘어나거나 줄어듬


  def bluffing(self):
 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@0617@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    #블러핑 시도 하기 1. 잔고 확인. 잔고에 따라 확률이 바뀜. 잔고 앞자리를 따라 y, n 개수가 변함. y 개수가 많으면 확률 증가, 리스트에서 하나 뽑아서 y면 블러핑 실행, n이면 일반
    # 2. 잔고가 3만 이상일 때, hand_check 결과가 3인 경우(special인 경우). 몬테카를로에 'good' 이하 수준 카드를 부여함.
    # 2. 잔고가 5만 이상일 때, hand_check 결과가 1인 경우(good 이하인 경우= 폴드해야 하는 경우), premium에 해당하는 카드를 몬테카를로에 부여함. 

    print('--------------Now MC Bluffing------------------')
    print('bluff: ', self.bluff)
    now_bal = str(self.bal) # 현재 잔고의 맨 앞자리를 계산한다. 
    y_count = int(now_bal[0])
    print("y_count , bluff.count('y')", y_count, self.bluff.count('y'))

    while y_count != self.bluff.count('y'): # 잔고 앞자리와 y 개수 맞추기
      print('working y')
      if y_count < self.bluff.count('y'): # 잔고 앞자리가 y 개수보다 작으면 y를 없앰
        self.bluff.pop(0)
        print(self.bluff)
      else:
        self.bluff.insert(0,'y') #잔고 앞자리가 y 개수보다 크면  y를 추가함.
        print(self.bluff)

    while len(self.bluff) != 10: # 리스트를 n으로 채워서 길이를 10으로 맞춤
      print('working len')
      if len(self.bluff)> 10:
        self.bluff.pop()
      else:
        self.bluff.append('n')

    card_rate = env.hand_check(self.hand1, self.hand2) #MC 카드 상태 확인

    if (self.bal>30000) and card_rate == 3:
      return (('s', 5),('s', 6))

    elif (self.bal>50000) and card_rate == 1:    
      return (('s', 9),('d', 9))
    
    else:
      return (self.hand1, self.hand2)


  def select_action(self, env):
    select_time = time.time()
    #가능한 행동 조사
    #self.count += 1
    #print('self.count: ',self.count)

    available_action = env.get_action()
    if (env.bet1>=0) and (env.bet2>= 2*env.bet1): #리레이즈의 상황이라면 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
      available_action = [-1, 0] #폴드하거나 콜만 함#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # 모든 카드의 경우의 수와 점수 쌍을 모을 딕셔너리 {'카드1,카드2,' : [0, 0, ... ,0]} 의 형태 
    Q_val_dict = {} 
    #print('MC available action', available_action)
    total_action = [-1, 0] # 게임에서 가능한 모든 행동 
    for i in range(200,2001):
      total_action.append(i)
    
    T = [] # 게임상 가능한 행동 개수만큼 0으로 채운 점수판 생성
    for i in range(1803):
      T.append(0)


    temp_p1 = Random_player() # 가상 게임용 플레이어 부여
    temp_p1.name = self.name # 이름과 잔고는 실제 플레이어 그대로 부여.
    temp_p1.bal = p1.bal

    temp_p2 = Random_player() # 가상 게임용 상대 플레이어 생성 
    temp_p2.name = temp_p2.name
    temp_p2.bal = p2.bal

    #가상 p1에 실제 카드 부여   
    temp_p1.hand1 = self.hand1
    temp_p1.hand2 = self.hand2

    if random.choice(self.bluff) == 'n': # n이 나오면 블러핑 시도 안 함. 
      temp_p1_deck = (temp_p1.hand1, temp_p1.hand2) # 시도 안하는 경우 실제 카드 그대로 부여.
    else:
      temp_p1_deck = self.bluffing() # 시도 하는 경우, 조건에 따라 다른 카드 부여.
    
   
    print('MC hands: ', self.hand1, self.hand2) # 확인용
    print('temp hands: ', temp_p1_deck)
     
    for i in range(len(available_action)):
      #플레이아웃을 1000번 반복
      for j in range(self.num_playout):

        #현재 상태를 복사해서 블레이 아웃에 사용
        temp_env = copy.deepcopy(env)
        
        deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
        random.shuffle(deck) # 플레이아웃용 deck 만들기 
        temp_env.deck = deck 
        temp_p2.hand1, temp_p2.hand2 = deck.pop(), deck.pop() # 상대방에게 임의로 카드 2장 부여 

        #print(temp_p1.hand1,temp_p1.hand2, temp_p2.hand1, temp_p2.hand2)  # 카드 확인
       
        #이전에 존재하지 않은 p1의 덱이라면 모든 행동 길이만큼의 점수판 리스트를 val 값으로 가짐
        if temp_p1_deck not in Q_val_dict.keys():
          Q_val_dict[temp_p1_deck] = T 
             
         # 가상 게임 실행, 현재 가능한 행동 안에서 루프를 수행함. 
        self.playout(temp_env, available_action[i], temp_p1, temp_p2) 
  
        #플레이 아웃의 결과는 승리 플레이어의 값으로 반환
        #p1이 이기면 reward = 1, p2가 이기면 reward = -1
        result_point = Q_val_dict[temp_p1_deck]  # 카드를 key로 값에 들어있는 리스트를 가져옴. 
       
        if temp_env.reward == 1: #p1이 승리한 경우
        # p1이 베팅한 금액이 게임상 가능한 액션 중에 몇 번째인지 점수판으로 가져와서 해당 인덱스에 +1
           # print(result_point[total_action.index(temp_env.bet1)])
          result_point[total_action.index(temp_env.bet1)] += 1 
         
    #print('result_point: ',  result_point)
     # 점수판에서 점수가 최대인 지점의 인덱스를 가져옴
    action_index = result_point.index(max(result_point))
    #print('action_index: ', action_index)
    # 게임상 가능한 모든 행동 리스트 중에서 가져온 인덱스에 있는 베팅값 제시 
    action = total_action[action_index] 

    if env.hand_check(self.hand1,self.hand2) <2: #MC 승률 높이기 용도. 애매한 카드면 미리 폴드  
      action=-1
    #print('MC aciton: ', action)
    # print('opponent bet: ', env.bet2 )
    #print('env.player_calls', env.player_calls)

    #print('len(avilable_action', len(available_action))
    if action == -1: #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
      if (len(available_action) <= 3) and (env.hand_check(self.hand1, self.hand2) >=2): # 승률 높이기 용 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        action = 0#@@@@@@@@@@@@ 리레이즈에서 쉽게 폴드하는 걸 방지
  
    if action == 0: # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
      if (env.player_calls == 0) and (env.last_bet==-2):
        action = 0
      elif env.player_calls == 1:
        action = env.last_bet# p1이 제시한 금액에 p2가 콜하는 경우 
      else:
        action = env.last_bet - env.bet1 #p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    if action == -1:
        pass
    else:
      self.bal -= action
    #수행시간 기록 
    if not self.select_time1:
        self.select_time1 = (time.time() - select_time)
    else:
        self.select_time2 = (time.time() - select_time)
    #print('MC select_time(s): %.3f'%(time.time() - select_time))
    #luck = 0 
    return action

  #플레이아웃 재귀 함수
  # 게임이 종료 상태(승/패/비김)가 될 때까지 행동을 임의로 선택하는 것을 반복
  def playout(self, temp_env, action,temp_p1, temp_p2):#, player):
    #판돈에 플레이어의 베팅을 반영 및 표시
  
    if temp_p1.name == 'MC Player':
      temp_env.bet1 = action
      temp_env.table += temp_env.bet1
    if temp_p2.name == 'MC Player':
      temp_env.bet2 = action
      temp_env.table += temp_env.bet2
    #print('temp_env.bet1,temp_env.bet2,temp_env.table',temp_env.bet1,temp_env.bet2,temp_env.table)
    temp_env.player_calls += 1
   # print('temp_env.endcheck', temp_env.player_calls)
    
    #가능한 행동 조사 
    #a무작위로 행동을 선택
    if temp_p1.name == 'MC Player':
      temp_env.bet2 = temp_p2.select_action(temp_env)
      if temp_env.player_calls >2:
        temp_env.bet2 = env.bet2
     # print('temp_env.bet2',temp_env.bet2)
      temp_env.table += temp_env.bet2
    if temp_p2.name == 'MC Player':
      temp_env.bet1 = temp_p1.select_action(temp_env)
      temp_env.table += temp_env.bet2
      if temp_env.player_calls >2:
        temmp_env.bet1 = env.bet1
    temp_env.player_calls += 1
   # print('temp_env.endcheck', temp_env.player_calls)

    #게임 종료 체크 
    if temp_env.player_calls >= 2:#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
     # print('temp_env.endcheck', temp_env.player_calls)
      temp_env.player_calls = 3#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
      temp_env.end_check(temp_p1, temp_p2)
      temp_env.player_calls =0

#베팅 금액별 프린트 
class Printer:
  
  def round_info(self, p1, p2, env): # p1.name, p2.name, p1.bal, p2.bal, ):
    if p1.name == 'MC Player':
      p = 'P1'
      balance = p1.bal
      select_time1 = p1.select_time1
      select_time2 = p1.select_time2

      
    if p2.name == 'MC Player':
      p = 'P2'
      balance = p2.bal
      select_time1 = p2.select_time1
      select_time2 = p2.select_time2
      
    if env.reward == 1:
      winner = 'P1'
    else:
      winner = 'P2'
    
    r = (p, balance, select_time1, select_time2, winner)

    f = open('round_info_100.csv', 'a', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(r)
    f.close()

  def after_round(self, game_time, p1,p2, p1_score, p2_score, draw_score, j):
    player = 'player'#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    win_rate = 0#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    balance = 0#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    if p1.name == 'MC Player':
      player = 'P1'
      balance = p1.bal
      win_rate = p1_score/(p1_score +p2_score + draw_score)

    if p2.name == 'MC Player':
      player = 'P2'
      balance = p2.bal
      win_rate = p2_score/(p1_score +p2_score + draw_score)

    complete_round = 1+j	
    
    r = (complete_round, game_time, player, win_rate, balance)
    
    f = open('after_round_100.csv', 'a', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(r)
    f.close()

p1 = Monte_Carlo_player()
#p1 = Random_player()
#p1 = Human_player()
p2 = Random_player()
#p2 = Monte_Carlo_player()
#p2 = Human_player()
prt = Printer()
# 지정된 게임 수를 자동으로 두게 할 것인지 한 게임씩 두게 할 것인지 결정
# auto = True : 지정된 판 수 (games)를 자동으로 진행
# auto = Flase: 한 게임씩 진행
auto = True

#auto 모드의 게임 수
games = 1000


#각 플레이어의 승리 횟수를 저장
p1_score = 0
p2_score = 0
draw_score = 0

start = time.time()
if auto:

    #자동모드 실행
    for j in range(games):
        np.random.seed(j)
        env = Environment()
        p1.hand1, p1.hand2 = env.deck.pop(), env.deck.pop()
        p2.hand1, p2.hand2 = env.deck.pop(), env.deck.pop()
        print('\n------------------------------------------------------------------------------------------------------------------')
        print("p1 player, money, hand : {} {} {}{}".format(p1.name, p1.bal, p1.hand1, p1.hand2))
        print("p2 player, money hand: {} {} {}{}".format(p2.name, p2.bal, p2.hand1, p2.hand2))
        
        if (p1.bal < 0) or (p2.bal <0):
          print('Player Balance Under 0, End this Game.\n')
          break
        for i in range(10000):
            sum = p1.bal+p2.bal
           
            reward, done = env.move(p1,p2) #,(-1)**i)
            print('각자 베팅',env.bet1, env.bet2)
            print('reward, done', reward, done)
            print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal+p2.bal))
            print('after move',sum, env.bet1, env.bet2)
            if sum != 100000:
              print('after move',sum, env.bet1, env.bet2)
              input()
            
            #prt.round_info(p1,p2,env) # 라운드 수행결과 프린트
            # 게임 종료 체크
            if done == True:
                if reward == 1:
                    print("j = {} winner is p1({})".format(j, p1.name))
                    p1_score += 1
                elif reward == -1:
                    print("j = {} winner is p2({})".format(j, p2.name))
                    p2_score += 1
                else:
                    print("j = {} winner is draw".format(j))
                    draw_score += 1
                break
    print("Good Game!")
    print("\n현재 라운드: {}\n{} 승리 횟수: {} {} 승리 횟수: {} 비긴 횟수: {}".format(j+1, p1.name, p1_score, p2.name, p2_score, draw_score))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal+p2.bal))
    game_time = time.time() - start
    print("수행 시간: {}".format(game_time))
    prt.after_round(game_time, p1, p2, p1_score, p2_score, draw_score, j)
    
else:
    #한 게임씩 진행하는 수동 모드
    while True:
        #env = Environment()
        env = Environment()
        p1.hand1, p1.hand2 = env.deck.pop(), env.deck.pop()
        p2.hand1, p2.hand2 = env.deck.pop(), env.deck.pop()
        print('------------------------------------------------------------------------------------------------------------------')
        print("p1 player, money, hand : {} {} {}{}".format(p1.name, p1.bal, p1.hand1, p1.hand2))
        print("p2 player, money hand: {} {} {}{}".format(p1.name, p2.bal, p2.hand1, p2.hand2))
        #print('------------------------------------------------------------------------------------------------------------------')
        #env.print = True

        for i in range(10000):
            # p1, p2 번갈아가면서 게임을 진행
            # p1(1) -> p2(-1)
            reward, done = env.move(p1, p2, (-1)**i)
            print('reward', reward)
            # 게임 종료 체크
            if done == True:
                if reward == 1:
                    print("Winner is p1({})".format(p1.name))
                    p1_score += 1
                elif reward == -1:
                    print("Winner is p2({})".format(p2.name))
                    p2_score += 1
                else:
                    print("No Winner")
                    draw_score += 1
                break

        print("final result")
        env.print_poker(p1)

        print("final result")
        env.print_poker(p2)

        # one more?
        answer = input("more Game? (y/n)")
        print("table= {} p1({}) = {} p2({}) = {} draw = {}".format(env.table, p1.name, p1_score, p2.name, p2_score, draw_score))
        if answer == 'y':
            pass
        else:
            print("Good Game!")
            print("\n현재 라운드: {}\n{} 승리 횟수: {} {} 승리 횟수: {} 비긴 횟수: {}".format(j+1, p1.name, p1_score, p2.name, p2_score, draw_score))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal+p2.bal))
            print("수행 시간: {}".format(time.time() - start))

