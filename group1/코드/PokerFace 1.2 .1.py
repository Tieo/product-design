# -*- conding: utf-8 -*-
import numpy as np
import random
import copy
import time
import pygame as pg


#할 일 :

class Environment:
    # 게임판 구성, 안되는 상태, 완료된 상태, 보상 정의
    # 게임판 핸드만 두장 줌, 베팅 한 번씩 물어봄. 리레이즈 1회만 가능

    # 덱을 만듬. 턴, 판돈, 플레이어가 베팅한 횟수 설정

    def __init__(self):
        self.done = False  # True면 게임 종료
        # self.winner = 0
        self.reward = 0
        self.turn = 0
        self.table = 0
        self.player_calls = 0
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
        # print('hc, a', handcheck, ai_action)
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

    def move(self, p1, p2):
        # 각플레이어가 선택한 행동 table에 반영하고 게임 상태 판단
        # p1 = 1, p2 = -1
        # 각 플레이어는 행동을 선택하는 메서드를 가짐 selct_action

        self.table += 400  # Blind
        p1.bal -= 200
        p2.bal -= 200

        self.bet1 = p1.select_action(env)  # 행동 선택 1
        self.last_bet = self.bet1
        if self.bet1 == -1:  # 폴드한 경우, 판돈에 돈을 넣지 않음
            pass
        else:
            self.table += self.bet1
        self.player_calls += 1  # p1 행동 카운트#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # else:
        self.bet2 = p2.select_action(env)  # , player) # p2 행동 선택
        self.last_bet = self.bet2
        if self.bet2 == -1:
            pass
        else:
            self.table += self.bet2  # p2의 금액 추가 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.player_calls += 1  # p2 의 행동 카운트 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if (self.bet1 >= 0) and (self.bet2 > self.bet1):  # 리레이즈
            # print('p1 action, p2 action', self.bet1, self.bet2)
            # self.player_calls += 1 # 확인
            self.bet1 = p1.select_action(env)  # 한번 더 행동을 받음 # 행동선택 3
            self.player_calls += 1  # 다시 p1 의 행동 카운트 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            self.last_bet = self.bet1
            if self.bet1 == -1:
                pass
            else:
                self.table += self.bet1

        else:
            self.player_calls += 1  # 행동 3번으로 맞추기 용도#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # print('table: {}, last_bet: {}'.format( self.table, self.last_bet))
        self.last_bet = -2  # 원상복구
        # 게임 상태가 종료인지 판단, 누가 이겼는지 체크
        # print('p calls', env.player_calls)
        self.end_check(p1, p2)
        self.player_calls = 0

        return self.reward, self.done

    # 현재 베팅 가능한 상태 수집.
    def get_action(self):
        observation = [-1, 0]
        # table이 0이 아니다. -> 누군가 베팅을 했다면 lowlimit 이 그 두배로 바뀜

        if self.last_bet > 0:
            if self.last_bet * 2 > 2000:
                self.lowlimit = 2000
            else:
                self.lowlimit = self.last_bet * 2
        # print('self.last_bet:{}, self.lowlimit:{}'.format(self.last_bet, self.lowlimit))
        for i in range(self.lowlimit, self.maxlimit + 1, 10):  # 이 부분 변경하면 경우의 수를 줄일 수 있음.
            observation.append(i)
        # print("in get action observation[] : ", observation)
        return observation

    # 게임 종료 판단
    def end_check(self, p1, p2):
        if (self.player_calls >= 3):  #

            # 판돈에 플레이어의 베팅을 반영 및 표시
            if (self.bet1 == -1):  # P1 폴드
                p2.bal += self.table
                self.table = 0
                self.reward = -1  # 승자는 p2
                self.done = True

            elif (self.bet2 == -1):  # P2 폴드
                p1.bal += self.table
                self.table = 0
                self.reward = 1  # 승자는 p1
                self.done = True

            else:  # 카드 점수 계산
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
                    p1.bal += self.table / 2
                    p2.bal += self.table / 2
                    self.table = 0
                    self.done = True  # 돈은 그대로 남아있음.
        else:
            pass
        return

    def print_poker(self, player):
        print('\n------------------Turn : %d-------------------\n' % self.turn)
        print('Table Money: %d' % self.table)
        print('Now Bet: %s' % player.name)

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
        # print('tup', tup)
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

    def select_action(self, env):  # ,player):

        Prefresh1()
        while True:
            available_action = env.get_action()
            action = None
            if (env.bet1 >= 0) and (
                    env.bet2 >= 2 * env.bet1):  # 리레이즈의 상황이라면  0614 changed from here @@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                available_action = [-1,
                                    0]  # env.bet2] #폴드하거나 p2 bet 콜만 함 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                # env.maxlimit = env.bet2
                '''print('possible action: ',
                      available_action)  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                print('{} Hands: {} {}'.format(self.name, self.hand1,
                                               self.hand2))  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                print('player_calls',
                      env.player_calls)  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
                '''action = int(input(
                    'fold: -1 , call: 0\n'))  # {}\n'.format(env.bet2)))#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
                for e in pg.event.get():
                    if e.type == pg.KEYDOWN:
                        if e.key == pg.K_UP:
                            action = 3
                            print("up")
                        elif e.key == pg.K_RIGHT:
                            action = 0
                            print("r")
                        elif e.key == pg.K_DOWN:
                            action = -1
                            print("d")
            else:  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                '''print('possible action: ',
                      available_action)  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                print('{} Hands: {} {}'.format(self.name, self.hand1,
                                               self.hand2))  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
                '''action = int(input('fold: -1, call: 0, {} <= raise <= {}\n'.format(env.lowlimit,
                                                                                   env.maxlimit)))  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''
                # until here @@@@@@@@@@@@@@@@@@@@@@@@
                for e in pg.event.get():
                    if e.type == pg.KEYDOWN:
                        if e.key == pg.K_UP:
                            action = 3
                            print("up")
                        elif e.key == pg.K_RIGHT:
                            action = 0
                            print("r")
                        elif e.key == pg.K_DOWN:
                            action = -1
                            print("d")
                if action == 3:
                    font = pg.font.Font(None, 50)  # 폰트 설정
                    screen.fill(BLACK)
                    line1 = font.render(('Type your bet(in 10 units)'), True, WHITE)
                    line2 = font.render((' Minimum %d Maximum %d ' % (env.lowlimit, env.maxlimit)), True, WHITE)
                    screen.blit(line2, (300, 350))
                    pg.display.flip()
                    text = ''
                    bet = 0
                    while 1:
                        for e in pg.event.get():
                            if e.type == pg.KEYDOWN:
                                if e.key == pg.K_RETURN:
                                    bet = text
                                    bet = int(bet)
                                    text = ''
                                    break
                                elif e.key == pg.K_BACKSPACE:
                                    screen.fill(BLACK)
                                    text = text[:-1]
                                else:
                                    screen.fill(BLACK)
                                    text += e.unicode
                        if env.lowlimit <= bet <= env.maxlimit:
                            break
                        block = font.render(text, True, WHITE)
                        rect = block.get_rect()
                        rect.center = screen.get_rect().center
                        screen.blit(block, rect)
                        pg.display.flip()
                    action = bet
            if action in available_action:
                if action == 0:  # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
                    if (env.player_calls == 0) and (env.last_bet == -2):
                        action = 0

                    elif env.player_calls == 1:
                        action = env.last_bet  # p1이 제시한 금액에 p2가 콜하는 경우
                    else:
                        action = env.last_bet - env.bet1  # p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

                if action == -1:
                    pass
                else:
                    self.bal -= action
                break  # 0614 break @@@@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            '''else:
                print("Wrong Action. Try Again")'''
        print('Human action: ', action)
        pg.time.wait(1000)
        Prefresh1()
        return action  # 0614 action @@@@@@@@@@@@@@@@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class Random_player:

    def __init__(self):
        self.name = 'Random Player'
        self.bal = 50000
        self.hand1 = 0
        self.hand2 = 0

    def select_action(self, env):

        available_action = env.get_action()


        # print(env.bet1)
        if (env.bet1 >= 0) and (
                env.bet2 >= 2 * env.bet1):  # 리레이즈의 상황이라면 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            available_action = [-1, 0]  # 폴드, 콜만 함#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        action = random.choice(available_action)  # 임의로 행동 선택

        # print('player_calls, available_action', env.player_calls, available_action)
        if action == 0:  # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
            if (env.player_calls == 0) and (env.last_bet == -2):
                action = 0
            elif env.player_calls == 1:
                action = env.last_bet  # p1이 제시한 금액에 p2가 콜하는 경우
            else:
                action = env.last_bet - env.bet1  # p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if action == -1:
            pass
        else:
            self.bal -= action
        # print("rand P action : ", action)


        return action


class Monte_Carlo_player:
    def __init__(self):
        self.name = "MC Player"
        self.num_playout = 10  # 최대 약 1300  예상, 덱에서 2장 뽑는 경우의 수 고려. # 80번 정도 할 때 승률, 속도 적당
        self.bal = 50000
        self.hand1 = 0
        self.hand2 = 0
        self.select_time1 = 0
        self.select_time2 = 0
        self.bluff = ['y', 'y', 'y', 'y', 'y', 'n', 'n', 'n', 'n', 'n']  # 블러핑 확률 계산용, 잔고 앞자리 숫자에 맞게 'y'가 늘어나거나 줄어듬

    def bluffing(self):
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@0617@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # 블러핑 시도 하기 1. 잔고 확인. 잔고에 따라 확률이 바뀜. 잔고 앞자리를 따라 y, n 개수가 변함. y 개수가 많으면 확률 증가, 리스트에서 하나 뽑아서 y면 블러핑 실행, n이면 일반
        # 2. 잔고가 3만 이상일 때, hand_check 결과가 3인 경우(special인 경우). 몬테카를로에 'good' 이하 수준 카드를 부여함.
        # 2. 잔고가 5만 이상일 때, hand_check 결과가 1인 경우(good 이하인 경우= 폴드해야 하는 경우), premium에 해당하는 카드를 몬테카를로에 부여함.

        print('--------------Now MC Bluffing------------------')
        print('bluff: ', self.bluff)
        now_bal = str(self.bal)  # 현재 잔고의 맨 앞자리를 계산한다.
        y_count = int(now_bal[0])
        print("y_count , bluff.count('y')", y_count, self.bluff.count('y'))

        while y_count != self.bluff.count('y'):  # 잔고 앞자리와 y 개수 맞추기
            print('working y')
            if y_count < self.bluff.count('y'):  # 잔고 앞자리가 y 개수보다 작으면 y를 없앰
                self.bluff.pop(0)
                print(self.bluff)
            else:
                self.bluff.insert(0, 'y')  # 잔고 앞자리가 y 개수보다 크면  y를 추가함.
                print(self.bluff)

        while len(self.bluff) != 10:  # 리스트를 n으로 채워서 길이를 10으로 맞춤
            print('working len')
            if len(self.bluff) > 10:
                self.bluff.pop()
            else:
                self.bluff.append('n')

        card_rate = env.hand_check(self.hand1, self.hand2)  # MC 카드 상태 확인

        if (self.bal > 30000) and card_rate == 3:
            return (('s', 5), ('s', 6))

        elif (self.bal > 50000) and card_rate == 1:
            return (('s', 9), ('d', 9))

        else:
            return (self.hand1, self.hand2)

    def select_action(self, env):
        select_time = time.time()
        # 가능한 행동 조사
        # self.count += 1
        # print('self.count: ',self.count)

        available_action = env.get_action()
        if (env.bet1 >= 0) and (
                env.bet2 >= 2 * env.bet1):  # 리레이즈의 상황이라면 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            available_action = [-1, 0]  # 폴드하거나 콜만 함#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # 모든 카드의 경우의 수와 점수 쌍을 모을 딕셔너리 {'카드1,카드2,' : [0, 0, ... ,0]} 의 형태
        Q_val_dict = {}
        # print('MC available action', available_action)
        total_action = [-1, 0]  # 게임에서 가능한 모든 행동
        for i in range(200, 2001):
            total_action.append(i)

        T = []  # 게임상 가능한 행동 개수만큼 0으로 채운 점수판 생성
        for i in range(1803):
            T.append(0)

        temp_p1 = Random_player()  # 가상 게임용 플레이어 부여
        temp_p1.name = self.name  # 이름과 잔고는 실제 플레이어 그대로 부여.
        temp_p1.bal = p1.bal

        temp_p2 = Random_player()  # 가상 게임용 상대 플레이어 생성
        temp_p2.name = temp_p2.name
        temp_p2.bal = p2.bal

        # 가상 p1에 실제 카드 부여
        temp_p1.hand1 = self.hand1
        temp_p1.hand2 = self.hand2

        if random.choice(self.bluff) == 'n':  # n이 나오면 블러핑 시도 안 함.
            temp_p1_deck = (temp_p1.hand1, temp_p1.hand2)  # 시도 안하는 경우 실제 카드 그대로 부여.
        else:
            temp_p1_deck = self.bluffing()  # 시도 하는 경우, 조건에 따라 다른 카드 부여.

        print('MC hands: ', self.hand1, self.hand2)  # 확인용
        print('temp hands: ', temp_p1_deck)

        for i in range(len(available_action)):
            # 플레이아웃을 1000번 반복
            for j in range(self.num_playout):

                # 현재 상태를 복사해서 블레이 아웃에 사용
                temp_env = copy.deepcopy(env)

                deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
                random.shuffle(deck)  # 플레이아웃용 deck 만들기
                temp_env.deck = deck
                temp_p2.hand1, temp_p2.hand2 = deck.pop(), deck.pop()  # 상대방에게 임의로 카드 2장 부여

                # print(temp_p1.hand1,temp_p1.hand2, temp_p2.hand1, temp_p2.hand2)  # 카드 확인

                # 이전에 존재하지 않은 p1의 덱이라면 모든 행동 길이만큼의 점수판 리스트를 val 값으로 가짐
                if temp_p1_deck not in Q_val_dict.keys():
                    Q_val_dict[temp_p1_deck] = T

                    # 가상 게임 실행, 현재 가능한 행동 안에서 루프를 수행함.
                self.playout(temp_env, available_action[i], temp_p1, temp_p2)

                # 플레이 아웃의 결과는 승리 플레이어의 값으로 반환
                # p1이 이기면 reward = 1, p2가 이기면 reward = -1
                result_point = Q_val_dict[temp_p1_deck]  # 카드를 key로 값에 들어있는 리스트를 가져옴.

                if temp_env.reward == 1:  # p1이 승리한 경우
                    # p1이 베팅한 금액이 게임상 가능한 액션 중에 몇 번째인지 점수판으로 가져와서 해당 인덱스에 +1
                    # print(result_point[total_action.index(temp_env.bet1)])
                    result_point[total_action.index(temp_env.bet1)] += 1

                    # print('result_point: ',  result_point)
        # 점수판에서 점수가 최대인 지점의 인덱스를 가져옴
        action_index = result_point.index(max(result_point))
        # print('action_index: ', action_index)
        # 게임상 가능한 모든 행동 리스트 중에서 가져온 인덱스에 있는 베팅값 제시
        action = total_action[action_index]

        if env.hand_check(self.hand1, self.hand2) < 2:  # MC 승률 높이기 용도. 애매한 카드면 미리 폴드
            action = -1
        # print('MC aciton: ', action)
        # print('opponent bet: ', env.bet2 )
        # print('env.player_calls', env.player_calls)

        # print('len(avilable_action', len(available_action))
        if action == -1:  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            if (len(available_action) <= 3) and (env.hand_check(self.hand1,
                                                                self.hand2) >= 2):  # 승률 높이기 용 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                action = 0  # @@@@@@@@@@@@ 리레이즈에서 쉽게 폴드하는 걸 방지

        if action == 0:  # 콜/체크라면 상대가 제시한 만큼 내게 됨. 추후 라운드 추가시 변경
            if (env.player_calls == 0) and (env.last_bet == -2):
                action = 0
            elif env.player_calls == 1:
                action = env.last_bet  # p1이 제시한 금액에 p2가 콜하는 경우
            else:
                action = env.last_bet - env.bet1  # p2가 제시한 금액에 p1이 콜하는 경우 #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        if action == -1:
            pass
        else:
            self.bal -= action
        # 수행시간 기록
        if not self.select_time1:
            self.select_time1 = (time.time() - select_time)
        else:
            self.select_time2 = (time.time() - select_time)
        # print('MC select_time(s): %.3f'%(time.time() - select_time))
        # luck = 0
        return action

    # 플레이아웃 재귀 함수
    # 게임이 종료 상태(승/패/비김)가 될 때까지 행동을 임의로 선택하는 것을 반복
    def playout(self, temp_env, action, temp_p1, temp_p2):  # , player):
        # 판돈에 플레이어의 베팅을 반영 및 표시

        if temp_p1.name == 'MC Player':
            temp_env.bet1 = action
            temp_env.table += temp_env.bet1
        if temp_p2.name == 'MC Player':
            temp_env.bet2 = action
            temp_env.table += temp_env.bet2
        # print('temp_env.bet1,temp_env.bet2,temp_env.table',temp_env.bet1,temp_env.bet2,temp_env.table)
        temp_env.player_calls += 1
        # print('temp_env.endcheck', temp_env.player_calls)

        # 가능한 행동 조사
        # a무작위로 행동을 선택
        if temp_p1.name == 'MC Player':
            temp_env.bet2 = temp_p2.select_action(temp_env)
            if temp_env.player_calls > 2:
                temp_env.bet2 = env.bet2
            # print('temp_env.bet2',temp_env.bet2)
            temp_env.table += temp_env.bet2
        if temp_p2.name == 'MC Player':
            temp_env.bet1 = temp_p1.select_action(temp_env)
            temp_env.table += temp_env.bet2
            if temp_env.player_calls > 2:
                temmp_env.bet1 = env.bet1
        temp_env.player_calls += 1
        # print('temp_env.endcheck', temp_env.player_calls)

        # 게임 종료 체크
        if temp_env.player_calls >= 2:  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            # print('temp_env.endcheck', temp_env.player_calls)
            temp_env.player_calls = 3  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            temp_env.end_check(temp_p1, temp_p2)
            temp_env.player_calls = 0





# 베팅 금액별 프린트
class Printer:

    def round_info(self, p1, p2, env):  # p1.name, p2.name, p1.bal, p2.bal, ):
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

    def after_round(self, game_time, p1, p2, p1_score, p2_score, draw_score, j):
        player = 'player'  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        win_rate = 0  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        balance = 0  # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        if p1.name == 'MC Player':
            player = 'P1'
            balance = p1.bal
            win_rate = p1_score / (p1_score + p2_score + draw_score)

        if p2.name == 'MC Player':
            player = 'P2'
            balance = p2.bal
            win_rate = p2_score / (p1_score + p2_score + draw_score)

        complete_round = 1 + j

        r = (complete_round, game_time, player, win_rate, balance)

        f = open('after_round_100.csv', 'a', encoding='utf-8', newline='')
        wr = csv.writer(f)
        wr.writerow(r)
        f.close()

def Prefresh1():
    global open
    for i in range(2, 15):
        if p1.hand1 == ('s', i):
            phand1 = sli[i-2]
        if p1.hand1 == ('h', i):
            phand1 = hli[i - 2]
        if p1.hand1 == ('d', i):
            phand1 = dli[i-2]
        if p1.hand1 == ('c', i):
            phand1 = cli[i-2]
        if p1.hand2 == ('s', i):
            phand2 = sli[i - 2]
        if p1.hand2 == ('h', i):
            phand2 = hli[i - 2]
        if p1.hand2 == ('d', i):
            phand2 = dli[i - 2]
        if p1.hand2 == ('c', i):
            phand2 = cli[i - 2]
        if p2.hand1 == ('s', i):
            ophand1 = sli[i-2]
        if p2.hand1 == ('h', i):
            ophand1 = hli[i - 2]
        if p2.hand1 == ('d', i):
            ophand1 = dli[i-2]
        if p2.hand1 == ('c', i):
            ophand1 = cli[i-2]
        if p2.hand2 == ('s', i):
            ophand2 = sli[i - 2]
        if p2.hand2 == ('h', i):
            ophand2 = hli[i - 2]
        if p2.hand2 == ('d', i):
            ophand2 = dli[i - 2]
        if p2.hand2 == ('c', i):
            ophand2 = cli[i - 2]
    font = pg.font.Font(None, 50)  # 폰트 설정
    screen.fill(BLACK)
    pmoney = font.render('{}'.format(int(p1.bal)), True, WHITE)
    if env.bet1 == -1:
        bet1 = 'fold'
    elif env.bet1 == -2:
        bet1 = 200
    else:
        bet1 = env.bet1

    ptable = font.render(str(bet1), True, WHITE)

    pname = font.render('{}'.format(p1.name), True, WHITE)
    print("p1 player, money, hand : {} {} {}{}".format(p1.name, p1.bal, p1.hand1, p1.hand2))
    screen.blit(pmoney, (480, 450))
    screen.blit(ptable, (500, 400))
    screen.blit(phand1, (430, 580))
    screen.blit(phand2, (540, 580))
    screen.blit(pname, (410, 520))
    if env.bet2 == -1:
        bet2 = 'fold'
    elif env.bet2 == -2:
        bet2 = 200
    else:
        bet2 = env.bet2
    opmoney = font.render('{}'.format(int(p2.bal)), True, WHITE)
    optable = font.render(str(bet2), True, WHITE)

    opname = font.render('{}'.format(p2.name), True, WHITE)

    screen.blit(opmoney, (480, 220))
    if bet1 != 'fold':
        screen.blit(optable, (500, 270))
    '''if turn == 4 and players[op1i][2] == 1:
        screen.blit(ophand1, (460, 50))
        screen.blit(ophand2, (510, 50))'''
    screen.blit(opname, (410, 140))
    if open == 1:
        screen.blit(ophand1, (430, 10))
        screen.blit(ophand2, (540, 10))
        pg.display.flip()
        pg.time.wait(4000)

    open = 0
    pg.display.flip()


class TextBox0(pg.sprite.Sprite):
  def __init__(self):
    pg.sprite.Sprite.__init__(self)
    self.text = ''
    self.font = pg.font.Font(None, 50)
    self.image = self.font.render('1 : Texas Holdem   2 : Mini Poker', False, [0, 0, 0])
    self.rect = self.image.get_rect()
  def add_chr(self, char):
    if char in validChars:
        self.text += char
    self.update()
  def update(self):
    old_rect_pos = self.rect.center
    self.image = self.font.render(self.text, False, [0, 0, 0])
    self.rect = self.image.get_rect()
    self.rect.center = old_rect_pos

class TextBox1(pg.sprite.Sprite):
  def __init__(self):
    pg.sprite.Sprite.__init__(self)
    self.text = ''
    self.font = pg.font.Font(None, 50)
    self.image = self.font.render('Set opponents 1~9', False, [0, 0, 0])
    self.rect = self.image.get_rect()
  def add_chr(self, char):
    if char in validChars:
        self.text += char
    self.update()
  def update(self):
    old_rect_pos = self.rect.center
    self.image = self.font.render(self.text, False, [0, 0, 0])
    self.rect = self.image.get_rect()
    self.rect.center = old_rect_pos

class TextBox2(pg.sprite.Sprite):
  def __init__(self):
    pg.sprite.Sprite.__init__(self)
    self.text = ''
    self.font = pg.font.Font(None, 50)
    self.image = self.font.render('1 : Random Player   2 : MC Player', False, [0, 0, 0])
    self.rect = self.image.get_rect()
  def add_chr(self, char):
    if char in validChars:
        self.text += char
    self.update()
  def update(self):
    old_rect_pos = self.rect.center
    self.image = self.font.render(self.text, False, [0, 0, 0])
    self.rect = self.image.get_rect()
    self.rect.center = old_rect_pos


def turnmove(turn):  ##누가 선일지 정하는 함수
    if len(players) == 2:
        print('dasdasd')
        players.append(players[0])
        del players[0]
    elif len(players) == 3:
        players.append(players[0])
        del players[0]
    elif len(players) == 4:
        for i in range(2):
            players.append(players[0])
            del players[0]
    elif len(players) == 5:
        for i in range(3):
            players.append(players[0])
            del players[0]
    elif len(players) == 6:
        for i in range(4):
            players.append(players[0])
            del players[0]
    elif len(players) == 7:
        for i in range(5):
            players.append(players[0])
            del players[0]
    elif len(players) == 8:
        for i in range(6):
            players.append(players[0])
            del players[0]
    elif len(players) == 9:
        for i in range(7):
            players.append(players[0])
            del players[0]
    elif len(players) == 10:
        for i in range(8):
            players.append(players[0])
            del players[0]

def Prefresh0(table, turn, pot, nowplay):
    font = pg.font.Font(None, 50)  # 폰트 설정
    screen.fill(BLACK)
    ccard = []
    for i in range(len(comcard)):
        for j in range(2, 15):
            if comcard[i] == ('s', j):
                ccard.append(sli[j-2])
            if comcard[i] == ('c', j):
                ccard.append(cli[j-2])
            if comcard[i] == ('d', j):
                ccard.append(dli[j-2])
            if comcard[i] == ('h', j):
                ccard.append(hli[j-2])
    if len(ccard) >= 3:
        screen.blit(ccard[0], (300, 300))
        screen.blit(ccard[1], (400, 300))
        screen.blit(ccard[2], (500, 300))
    if len(ccard) >= 4:
        screen.blit(ccard[3], (600, 300))
    if len(ccard) == 5:
        screen.blit(ccard[4], (700, 300))
    font = pg.font.Font(None, 30)
    potmoney = font.render(str(pot), True, WHITE)
    turnmark = font.render('TURN', True, RED)
    screen.blit(potmoney, (520, 440))
    font = pg.font.Font(None, 20)
    db = font.render('DB', True, RED)
    phand = []
    op1hand = []
    op2hand = []
    op3hand = []
    op4hand = []
    op5hand = []
    op6hand = []
    op7hand = []
    op8hand = []
    op9hand = []

    if len(players) == 2:
        for i in range(2):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
        if nowplay == pi:
            screen.blit(turnmark, (600, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (300, 160))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i+5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i+5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i+5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i+5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 0:
            screen.blit(db, (495, 610))
        if turn > 0 and pi == 2:
            screen.blit(db, (495, 610))
        screen.blit(pmoney, (480, 650))
        screen.blit(ppf, (480, 630))
        screen.blit(ptable, (500, 500))
        screen.blit(phand[0], (600, 600))
        screen.blit(phand[1], (650, 600))
        screen.blit(pname, (480, 700))

        opmoney = font.render(str(players[op1i][1]), True, WHITE)
        optable = font.render(str(table[op1i]), True, WHITE)
        opname = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            oppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            oppf = font.render(fold, True, RED)
        if turn == 0 and op1i == 0:
            screen.blit(db, (495, 110))
        if turn > 0 and op1i == 2:
            screen.blit(db, (495, 110))
        screen.blit(opmoney, (480, 70))
        screen.blit(oppf, (480, 90))
        screen.blit(optable, (500, 220))
        screen.blit(back, (300, 10))
        screen.blit(back, (350, 10))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (300, 10))
            screen.blit(op1hand[1], (350, 10))
        screen.blit(opname, (480, 20))

    elif len(players) == 3:
        for i in range(3):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
        if nowplay == pi:
            screen.blit(turnmark, (600, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (50, 160))
        elif nowplay == op2i:
            screen.blit(turnmark, (900, 160))

        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            oppf = font.render(fold, True, RED)
        if turn == 0 and pi == 0:
            screen.blit(db, (495, 610))
        if turn > 0 and pi == 2:
            screen.blit(db, (495, 610))
        screen.blit(pmoney, (480, 650))
        screen.blit(ppf, (480, 630))
        screen.blit(ptable, (500, 500))
        screen.blit(phand[0], (600, 600))
        screen.blit(phand[1], (650, 600))
        screen.blit(pname, (480, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 0:
            screen.blit(db, (235, 110))
        if turn > 0 and op1i == 1:
            screen.blit(db, (235, 110))
        screen.blit(op1money, (230, 70))
        screen.blit(op1pf, (230, 90))
        screen.blit(op1table, (250, 220))
        screen.blit(back, (50, 10))
        screen.blit(back, (100, 10))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (50, 10))
            screen.blit(op1hand[1], (100, 10))
        screen.blit(op1name, (230, 20))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)
        op2hand1 = font.render(str(players[op2i][5]), True, WHITE)
        op2hand2 = font.render(str(players[op2i][6]), True, WHITE)
        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 0:
            screen.blit(db, (785, 110))
        if turn > 0 and op2i == 2:
            screen.blit(db, (785, 110))
        screen.blit(op2money, (780, 70))
        screen.blit(op2pf, (780, 90))
        screen.blit(op2table, (800, 220))
        screen.blit(back, (900, 10))
        screen.blit(back, (950, 10))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (900, 10))
            screen.blit(op2hand[1], (950, 10))
        screen.blit(op2name, (780, 20))

    elif len(players) == 4:
        for i in range(4):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
        if nowplay == pi:
            screen.blit(turnmark, (800, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op3i:
            screen.blit(turnmark, (800, 160))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)

        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 1:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 3:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (900, 500))
        screen.blit(phand[0], (800, 600))
        screen.blit(phand[1], (850, 600))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)

        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 1:
            screen.blit(db, (55, 610))
        if turn > 0 and op1i == 3:
            screen.blit(db, (55, 610))
        screen.blit(op1money, (50, 650))
        screen.blit(op1pf, (50, 630))
        screen.blit(op1table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (120, 600))
            screen.blit(op1hand[1], (170, 600))
        screen.blit(op1name, (20, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)
        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 1:
            screen.blit(db, (55, 120))
        if turn > 0 and op2i == 3:
            screen.blit(db, (55, 120))
        screen.blit(op2money, (50, 80))
        screen.blit(op2pf, (50, 100))
        screen.blit(op2table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (120, 10))
            screen.blit(op2hand[1], (170, 10))
        screen.blit(op2name, (20, 20))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)
        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 1:
            screen.blit(db, (985, 120))
        if turn > 0 and op3i == 3:
            screen.blit(db, (985, 120))
        screen.blit(op3money, (980, 80))
        screen.blit(op3pf, (980, 100))
        screen.blit(op3table, (900, 250))
        screen.blit(back, (800, 10))
        screen.blit(back, (850, 10))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (800, 10))
            screen.blit(op3hand[1], (850, 10))
        screen.blit(op3name, (960, 20))

    elif len(players) == 5:
        for i in range(5):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (550, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op4i:
            screen.blit(turnmark, (800, 160))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 2:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 4:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (900, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 2:
            screen.blit(db, (485, 610))
        if turn > 0 and op1i == 4:
            screen.blit(db, (485, 610))
        screen.blit(op1money, (480, 650))
        screen.blit(op1pf, (480, 630))
        screen.blit(op1table, (480, 500))
        screen.blit(back, (550, 600))
        screen.blit(back, (600, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (550, 600))
            screen.blit(op1hand[1], (600, 600))
        screen.blit(op1name, (480, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)

        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 2:
            screen.blit(db, (55, 610))
        if turn > 0 and op2i == 4:
            screen.blit(db, (55, 610))
        screen.blit(op2money, (50, 650))
        screen.blit(op2pf, (50, 630))
        screen.blit(op2table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (120, 600))
            screen.blit(op2hand[1], (170, 600))
        screen.blit(op2name, (20, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)
        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 2:
            screen.blit(db, (55, 120))
        if turn > 0 and op3i == 4:
            screen.blit(db, (55, 120))
        screen.blit(op3money, (50, 80))
        screen.blit(op3pf, (50, 100))
        screen.blit(op3table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (120, 10))
            screen.blit(op3hand[1], (170, 10))
        screen.blit(op3name, (20, 20))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 2:
            screen.blit(db, (985, 120))
        if turn > 0 and op4i == 4:
            screen.blit(db, (985, 120))
        screen.blit(op4money, (980, 80))
        screen.blit(op4pf, (980, 100))
        screen.blit(op4table, (900, 250))
        screen.blit(back, (850, 10))
        screen.blit(back, (800, 10))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (850, 10))
            screen.blit(op4hand[1], (800, 10))
        screen.blit(op4name, (960, 20))

    elif len(players) == 6:
        for i in range(6):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
            if players[i][0] == 'opponent5':
                op5i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (550, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op4i:
            screen.blit(turnmark, (550, 160))
        elif nowplay == op5i:
            screen.blit(turnmark, (800, 160))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
                if players[op5i][i + 5] == ('s', j):
                    op5hand.append(sli[j - 2])
                if players[op5i][i + 5] == ('c', j):
                    op5hand.append(cli[j - 2])
                if players[op5i][i + 5] == ('d', j):
                    op5hand.append(dli[j - 2])
                if players[op5i][i + 5] == ('h', j):
                    op5hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 3:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 5:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (900, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 3:
            screen.blit(db, (485, 610))
        if turn > 0 and op1i == 5:
            screen.blit(db, (485, 610))
        screen.blit(op1money, (480, 650))
        screen.blit(op1pf, (480, 630))
        screen.blit(op1table, (480, 500))
        screen.blit(back, (550, 600))
        screen.blit(back, (600, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (550, 600))
            screen.blit(op1hand[1], (600, 600))
        screen.blit(op1name, (480, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)

        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 3:
            screen.blit(db, (55, 610))
        if turn > 0 and op2i == 5:
            screen.blit(db, (55, 610))
        screen.blit(op2money, (50, 650))
        screen.blit(op2pf, (50, 630))
        screen.blit(op2table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (120, 600))
            screen.blit(op2hand[1], (170, 600))
        screen.blit(op2name, (20, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)
        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 3:
            screen.blit(db, (55, 120))
        if turn > 0 and op3i == 5:
            screen.blit(db, (55, 120))
        screen.blit(op3money, (50, 80))
        screen.blit(op3pf, (50, 100))
        screen.blit(op3table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (120, 10))
            screen.blit(op3hand[1], (170, 10))
        screen.blit(op3name, (20, 20))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 3:
            screen.blit(db, (485, 120))
        if turn > 0 and op4i == 5:
            screen.blit(db, (485, 120))
        screen.blit(op4money, (480, 80))
        screen.blit(op4pf, (480, 100))
        screen.blit(op4table, (480, 250))
        screen.blit(back, (550, 10))
        screen.blit(back, (600, 10))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (550, 10))
            screen.blit(op4hand[1], (600, 10))
        screen.blit(op4name, (480, 20))

        op5money = font.render(str(players[op5i][1]), True, WHITE)
        op5table = font.render(str(table[op5i]), True, WHITE)
        op5name = font.render(str(players[op5i][0]), True, WHITE)
        if players[op5i][2] == 1:
            fold = "Playing"
            op5pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op5pf = font.render(fold, True, RED)
        if turn == 0 and op5i == 3:
            screen.blit(db, (985, 120))
        if turn > 0 and op5i == 5:
            screen.blit(db, (985, 120))
        screen.blit(op5money, (980, 80))
        screen.blit(op5pf, (980, 100))
        screen.blit(op5table, (900, 250))
        screen.blit(back, (850, 10))
        screen.blit(back, (800, 10))
        if turn == 4 and players[op5i][2] == 1:
            screen.blit(op5hand[0], (850, 10))
            screen.blit(op5hand[1], (800, 10))
        screen.blit(op5name, (960, 20))

    elif len(players) == 7:
        for i in range(7):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
            if players[i][0] == 'opponent5':
                op5i = i
            if players[i][0] == 'opponent6':
                op6i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (550, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (90, 310))
        elif nowplay == op4i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op5i:
            screen.blit(turnmark, (550, 160))
        elif nowplay == op6i:
            screen.blit(turnmark, (800, 160))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
                if players[op5i][i + 5] == ('s', j):
                    op5hand.append(sli[j - 2])
                if players[op5i][i + 5] == ('c', j):
                    op5hand.append(cli[j - 2])
                if players[op5i][i + 5] == ('d', j):
                    op5hand.append(dli[j - 2])
                if players[op5i][i + 5] == ('h', j):
                    op5hand.append(hli[j - 2])
                if players[op6i][i + 5] == ('s', j):
                    op6hand.append(sli[j - 2])
                if players[op6i][i + 5] == ('c', j):
                    op6hand.append(cli[j - 2])
                if players[op6i][i + 5] == ('d', j):
                    op6hand.append(dli[j - 2])
                if players[op6i][i + 5] == ('h', j):
                    op6hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 4:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 6:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (860, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 4:
            screen.blit(db, (485, 610))
        if turn > 0 and op1i == 6:
            screen.blit(db, (485, 610))
        screen.blit(op1money, (480, 650))
        screen.blit(op1pf, (480, 630))
        screen.blit(op1table, (480, 500))
        screen.blit(back, (550, 600))
        screen.blit(back, (600, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (550, 600))
            screen.blit(op1hand[1], (600, 600))
        screen.blit(op1name, (480, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)

        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 4:
            screen.blit(db, (55, 610))
        if turn > 0 and op2i == 6:
            screen.blit(db, (55, 610))
        screen.blit(op2money, (50, 650))
        screen.blit(op2pf, (50, 630))
        screen.blit(op2table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (120, 600))
            screen.blit(op2hand[1], (170, 600))
        screen.blit(op2name, (20, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)
        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 4:
            screen.blit(db, (80, 300))
        if turn > 0 and op3i == 6:
            screen.blit(db, (80, 300))
        screen.blit(op3money, (10, 320))
        screen.blit(op3pf, (10, 300))
        screen.blit(op3table, (180, 370))
        screen.blit(back, (10, 340))
        screen.blit(back, (60, 340))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (10, 340))
            screen.blit(op3hand[1], (60, 340))
        screen.blit(op3name, (10, 280))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 4:
            screen.blit(db, (55, 120))
        if turn > 0 and op4i == 6:
            screen.blit(db, (55, 120))
        screen.blit(op4money, (50, 80))
        screen.blit(op4pf, (50, 100))
        screen.blit(op4table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (120, 10))
            screen.blit(op4hand[1], (170, 10))
        screen.blit(op4name, (20, 20))

        op5money = font.render(str(players[op5i][1]), True, WHITE)
        op5table = font.render(str(table[op5i]), True, WHITE)
        op5name = font.render(str(players[op5i][0]), True, WHITE)
        if players[op5i][2] == 1:
            fold = "Playing"
            op5pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op5pf = font.render(fold, True, RED)
        if turn == 0 and op5i == 4:
            screen.blit(db, (485, 120))
        if turn > 0 and op5i == 6:
            screen.blit(db, (485, 120))
        screen.blit(op5money, (480, 80))
        screen.blit(op5pf, (480, 100))
        screen.blit(op5table, (480, 250))
        screen.blit(back, (550, 10))
        screen.blit(back, (600, 10))
        if turn == 4 and players[op5i][2] == 1:
            screen.blit(op5hand[0], (550, 10))
            screen.blit(op5hand[1], (600, 10))
        screen.blit(op5name, (480, 20))

        op6money = font.render(str(players[op6i][1]), True, WHITE)
        op6table = font.render(str(table[op6i]), True, WHITE)
        op6name = font.render(str(players[op6i][0]), True, WHITE)
        if players[op6i][2] == 1:
            fold = "Playing"
            op6pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op6pf = font.render(fold, True, RED)
        if turn == 0 and op6i == 4:
            screen.blit(db, (985, 120))
        if turn > 0 and op6i == 6:
            screen.blit(db, (985, 120))
        screen.blit(op6money, (980, 80))
        screen.blit(op6pf, (980, 100))
        screen.blit(op6table, (860, 250))
        screen.blit(back, (850, 10))
        screen.blit(back, (800, 10))
        if turn == 4 and players[op6i][2] == 1:
            screen.blit(op6hand[0], (850, 10))
            screen.blit(op6hand[1], (800, 10))
        screen.blit(op6name, (960, 20))

    elif len(players) == 8:
        for i in range(8):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
            if players[i][0] == 'opponent5':
                op5i = i
            if players[i][0] == 'opponent6':
                op6i = i
            if players[i][0] == 'opponent7':
                op7i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (550, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (90, 310))
        elif nowplay == op4i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op5i:
            screen.blit(turnmark, (550, 160))
        elif nowplay == op6i:
            screen.blit(turnmark, (800, 160))
        elif nowplay == op7i:
            screen.blit(turnmark, (950, 310))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
                if players[op5i][i + 5] == ('s', j):
                    op5hand.append(sli[j - 2])
                if players[op5i][i + 5] == ('c', j):
                    op5hand.append(cli[j - 2])
                if players[op5i][i + 5] == ('d', j):
                    op5hand.append(dli[j - 2])
                if players[op5i][i + 5] == ('h', j):
                    op5hand.append(hli[j - 2])
                if players[op6i][i + 5] == ('s', j):
                    op6hand.append(sli[j - 2])
                if players[op6i][i + 5] == ('c', j):
                    op6hand.append(cli[j - 2])
                if players[op6i][i + 5] == ('d', j):
                    op6hand.append(dli[j - 2])
                if players[op6i][i + 5] == ('h', j):
                    op6hand.append(hli[j - 2])
                if players[op7i][i + 5] == ('s', j):
                    op7hand.append(sli[j - 2])
                if players[op7i][i + 5] == ('c', j):
                    op7hand.append(cli[j - 2])
                if players[op7i][i + 5] == ('d', j):
                    op7hand.append(dli[j - 2])
                if players[op7i][i + 5] == ('h', j):
                    op7hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 5:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 7:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (860, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 5:
            screen.blit(db, (485, 610))
        if turn > 0 and op1i == 7:
            screen.blit(db, (485, 610))
        screen.blit(op1money, (480, 650))
        screen.blit(op1pf, (480, 630))
        screen.blit(op1table, (480, 500))
        screen.blit(back, (550, 600))
        screen.blit(back, (600, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (550, 600))
            screen.blit(op1hand[1], (600, 600))
        screen.blit(op1name, (480, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)

        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 5:
            screen.blit(db, (55, 610))
        if turn > 0 and op2i == 7:
            screen.blit(db, (55, 610))
        screen.blit(op2money, (50, 650))
        screen.blit(op2pf, (50, 630))
        screen.blit(op2table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (120, 600))
            screen.blit(op2hand[1], (170, 600))
        screen.blit(op2name, (20, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)
        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 5:
            screen.blit(db, (80, 300))
        if turn > 0 and op3i == 7:
            screen.blit(db, (80, 300))
        screen.blit(op3money, (10, 320))
        screen.blit(op3pf, (10, 300))
        screen.blit(op3table, (180, 370))
        screen.blit(back, (10, 340))
        screen.blit(back, (60, 340))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (10, 340))
            screen.blit(op3hand[1], (60, 340))
        screen.blit(op3name, (10, 280))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 5:
            screen.blit(db, (55, 120))
        if turn > 0 and op4i == 7:
            screen.blit(db, (55, 120))
        screen.blit(op4money, (50, 80))
        screen.blit(op4pf, (50, 100))
        screen.blit(op4table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (120, 10))
            screen.blit(op4hand[1], (170, 10))
        screen.blit(op4name, (20, 20))

        op5money = font.render(str(players[op5i][1]), True, WHITE)
        op5table = font.render(str(table[op5i]), True, WHITE)
        op5name = font.render(str(players[op5i][0]), True, WHITE)
        if players[op5i][2] == 1:
            fold = "Playing"
            op5pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op5pf = font.render(fold, True, RED)
        if turn == 0 and op5i == 5:
            screen.blit(db, (485, 120))
        if turn > 0 and op5i == 7:
            screen.blit(db, (485, 120))
        screen.blit(op5money, (480, 80))
        screen.blit(op5pf, (480, 100))
        screen.blit(op5table, (480, 250))
        screen.blit(back, (550, 10))
        screen.blit(back, (600, 10))
        if turn == 4 and players[op5i][2] == 1:
            screen.blit(op5hand[0], (550, 10))
            screen.blit(op5hand[1], (600, 10))
        screen.blit(op5name, (480, 20))

        op6money = font.render(str(players[op6i][1]), True, WHITE)
        op6table = font.render(str(table[op6i]), True, WHITE)
        op6name = font.render(str(players[op6i][0]), True, WHITE)
        if players[op6i][2] == 1:
            fold = "Playing"
            op6pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op6pf = font.render(fold, True, RED)
        if turn == 0 and op6i == 5:
            screen.blit(db, (985, 120))
        if turn > 0 and op6i == 7:
            screen.blit(db, (985, 120))
        screen.blit(op6money, (980, 80))
        screen.blit(op6pf, (980, 100))
        screen.blit(op6table, (860, 250))
        screen.blit(back, (850, 10))
        screen.blit(back, (800, 10))
        if turn == 4 and players[op6i][2] == 1:
            screen.blit(op6hand[0], (850, 10))
            screen.blit(op6hand[1], (800, 10))
        screen.blit(op6name, (960, 20))

        op7money = font.render(str(players[op7i][1]), True, WHITE)
        op7table = font.render(str(table[op7i]), True, WHITE)
        op7name = font.render(str(players[op7i][0]), True, WHITE)
        if players[op7i][2] == 1:
            fold = "Playing"
            op7pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op7pf = font.render(fold, True, RED)
        if turn == 0 and op7i == 5:
            screen.blit(db, (975, 300))
        if turn > 0 and op7i == 7:
            screen.blit(db, (975, 300))
        screen.blit(op7money, (1030, 320))
        screen.blit(op7pf, (1030, 300))
        screen.blit(op7table, (860, 370))
        screen.blit(back, (950, 340))
        screen.blit(back, (1000, 340))
        if turn == 4 and players[op7i][2] == 1:
            screen.blit(op7hand[0], (950, 340))
            screen.blit(op7hand[1], (1000, 340))
        screen.blit(op7name, (1010, 280))

    elif len(players) == 9:
        for i in range(9):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
            if players[i][0] == 'opponent5':
                op5i = i
            if players[i][0] == 'opponent6':
                op6i = i
            if players[i][0] == 'opponent7':
                op7i = i
            if players[i][0] == 'opponent8':
                op8i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (730, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (430, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op4i:
            screen.blit(turnmark, (90, 310))
        elif nowplay == op5i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op6i:
            screen.blit(turnmark, (550, 160))
        elif nowplay == op7i:
            screen.blit(turnmark, (800, 160))
        elif nowplay == op8i:
            screen.blit(turnmark, (950, 310))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
                if players[op5i][i + 5] == ('s', j):
                    op5hand.append(sli[j - 2])
                if players[op5i][i + 5] == ('c', j):
                    op5hand.append(cli[j - 2])
                if players[op5i][i + 5] == ('d', j):
                    op5hand.append(dli[j - 2])
                if players[op5i][i + 5] == ('h', j):
                    op5hand.append(hli[j - 2])
                if players[op6i][i + 5] == ('s', j):
                    op6hand.append(sli[j - 2])
                if players[op6i][i + 5] == ('c', j):
                    op6hand.append(cli[j - 2])
                if players[op6i][i + 5] == ('d', j):
                    op6hand.append(dli[j - 2])
                if players[op6i][i + 5] == ('h', j):
                    op6hand.append(hli[j - 2])
                if players[op7i][i + 5] == ('s', j):
                    op7hand.append(sli[j - 2])
                if players[op7i][i + 5] == ('c', j):
                    op7hand.append(cli[j - 2])
                if players[op7i][i + 5] == ('d', j):
                    op7hand.append(dli[j - 2])
                if players[op7i][i + 5] == ('h', j):
                    op7hand.append(hli[j - 2])
                if players[op8i][i + 5] == ('s', j):
                    op8hand.append(sli[j - 2])
                if players[op8i][i + 5] == ('c', j):
                    op8hand.append(cli[j - 2])
                if players[op8i][i + 5] == ('d', j):
                    op8hand.append(dli[j - 2])
                if players[op8i][i + 5] == ('h', j):
                    op8hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 6:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 8:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (860, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 6:
            screen.blit(db, (665, 610))
        if turn > 0 and op1i == 8:
            screen.blit(db, (665, 610))
        screen.blit(op1money, (660, 650))
        screen.blit(op1pf, (660, 630))
        screen.blit(op1table, (660, 500))
        screen.blit(back, (730, 600))
        screen.blit(back, (780, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (730, 600))
            screen.blit(op1hand[1], (780, 600))
        screen.blit(op1name, (660, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)
        op2hand1 = font.render(str(players[op2i][5]), True, WHITE)
        op2hand2 = font.render(str(players[op2i][6]), True, WHITE)
        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 6:
            screen.blit(db, (355, 610))
        if turn > 0 and op2i == 8:
            screen.blit(db, (355, 610))
        screen.blit(op2money, (350, 650))
        screen.blit(op2pf, (350, 630))
        screen.blit(op2table, (350, 500))
        screen.blit(back, (430, 600))
        screen.blit(back, (480, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (430, 600))
            screen.blit(op2hand[1], (480, 600))
        screen.blit(op2name, (350, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)

        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 6:
            screen.blit(db, (55, 610))
        if turn > 0 and op3i == 8:
            screen.blit(db, (55, 610))
        screen.blit(op3money, (50, 650))
        screen.blit(op3pf, (50, 630))
        screen.blit(op3table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (120, 600))
            screen.blit(op3hand[1], (170, 600))
        screen.blit(op3name, (20, 700))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 6:
            screen.blit(db, (80, 300))
        if turn > 0 and op4i == 8:
            screen.blit(db, (80, 300))
        screen.blit(op4money, (10, 320))
        screen.blit(op4pf, (10, 300))
        screen.blit(op4table, (180, 370))
        screen.blit(back, (10, 340))
        screen.blit(back, (60, 340))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (10, 340))
            screen.blit(op4hand[1], (60, 340))
        screen.blit(op4name, (10, 280))

        op5money = font.render(str(players[op5i][1]), True, WHITE)
        op5table = font.render(str(table[op5i]), True, WHITE)
        op5name = font.render(str(players[op5i][0]), True, WHITE)
        if players[op5i][2] == 1:
            fold = "Playing"
            op5pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op5pf = font.render(fold, True, RED)
        if turn == 0 and op5i == 6:
            screen.blit(db, (55, 120))
        if turn > 0 and op5i == 8:
            screen.blit(db, (55, 120))
        screen.blit(op5money, (50, 80))
        screen.blit(op5pf, (50, 100))
        screen.blit(op5table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op5i][2] == 1:
            screen.blit(op5hand[0], (120, 10))
            screen.blit(op5hand[1], (170, 10))
        screen.blit(op5name, (20, 20))

        op6money = font.render(str(players[op6i][1]), True, WHITE)
        op6table = font.render(str(table[op6i]), True, WHITE)
        op6name = font.render(str(players[op6i][0]), True, WHITE)
        if players[op6i][2] == 1:
            fold = "Playing"
            op6pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op6pf = font.render(fold, True, RED)
        if turn == 0 and op6i == 6:
            screen.blit(db, (485, 120))
        if turn > 0 and op6i == 8:
            screen.blit(db, (485, 120))
        screen.blit(op6money, (480, 80))
        screen.blit(op6pf, (480, 100))
        screen.blit(op6table, (480, 250))
        screen.blit(back, (550, 10))
        screen.blit(back, (600, 10))
        if turn == 4 and players[op6i][2] == 1:
            screen.blit(op6hand[0], (550, 10))
            screen.blit(op6hand[1], (600, 10))
        screen.blit(op6name, (480, 20))

        op7money = font.render(str(players[op7i][1]), True, WHITE)
        op7table = font.render(str(table[op7i]), True, WHITE)
        op7name = font.render(str(players[op7i][0]), True, WHITE)
        if players[op7i][2] == 1:
            fold = "Playing"
            op7pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op7pf = font.render(fold, True, RED)
        if turn == 0 and op7i == 6:
            screen.blit(db, (985, 120))
        if turn > 0 and op7i == 8:
            screen.blit(db, (985, 120))
        screen.blit(op7money, (980, 80))
        screen.blit(op7pf, (980, 100))
        screen.blit(op7table, (860, 250))
        screen.blit(back, (850, 10))
        screen.blit(back, (800, 10))
        if turn == 4 and players[op7i][2] == 1:
            screen.blit(op7hand[0], (850, 10))
            screen.blit(op7hand[1], (800, 10))
        screen.blit(op7name, (960, 20))

        op8money = font.render(str(players[op8i][1]), True, WHITE)
        op8table = font.render(str(table[op8i]), True, WHITE)
        op8name = font.render(str(players[op8i][0]), True, WHITE)
        if players[op8i][2] == 1:
            fold = "Playing"
            op8pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op8pf = font.render(fold, True, RED)
        if turn == 0 and op8i == 6:
            screen.blit(db, (975, 300))
        if turn > 0 and op8i == 8:
            screen.blit(db, (975, 300))
        screen.blit(op8money, (1030, 320))
        screen.blit(op8pf, (1030, 300))
        screen.blit(op8table, (860, 370))
        screen.blit(back, (950, 340))
        screen.blit(back, (1000, 340))
        if turn == 4 and players[op8i][2] == 1:
            screen.blit(op8hand[0], (950, 340))
            screen.blit(op8hand[1], (1000, 340))
        screen.blit(op8name, (1010, 280))

    elif len(players) == 10:
        for i in range(10):
            if players[i][0] == 'player':
                pi = i
            if players[i][0] == 'opponent1':
                op1i = i
            if players[i][0] == 'opponent2':
                op2i = i
            if players[i][0] == 'opponent3':
                op3i = i
            if players[i][0] == 'opponent4':
                op4i = i
            if players[i][0] == 'opponent5':
                op5i = i
            if players[i][0] == 'opponent6':
                op6i = i
            if players[i][0] == 'opponent7':
                op7i = i
            if players[i][0] == 'opponent8':
                op8i = i
            if players[i][0] == 'opponent9':
                op9i = i
        if nowplay == pi:
            screen.blit(turnmark, (950, 560))
        elif nowplay == op1i:
            screen.blit(turnmark, (730, 560))
        elif nowplay == op2i:
            screen.blit(turnmark, (430, 560))
        elif nowplay == op3i:
            screen.blit(turnmark, (120, 560))
        elif nowplay == op4i:
            screen.blit(turnmark, (90, 310))
        elif nowplay == op5i:
            screen.blit(turnmark, (120, 160))
        elif nowplay == op6i:
            screen.blit(turnmark, (430, 160))
        elif nowplay == op7i:
            screen.blit(turnmark, (730, 160))
        elif nowplay == op8i:
            screen.blit(turnmark, (930, 160))
        elif nowplay == op9i:
            screen.blit(turnmark, (950, 310))
        for i in range(2):
            for j in range(2, 15):
                if players[pi][i + 5] == ('s', j):
                    phand.append(sli[j - 2])
                if players[pi][i + 5] == ('c', j):
                    phand.append(cli[j - 2])
                if players[pi][i + 5] == ('d', j):
                    phand.append(dli[j - 2])
                if players[pi][i + 5] == ('h', j):
                    phand.append(hli[j - 2])
                if players[op1i][i + 5] == ('s', j):
                    op1hand.append(sli[j - 2])
                if players[op1i][i + 5] == ('c', j):
                    op1hand.append(cli[j - 2])
                if players[op1i][i + 5] == ('d', j):
                    op1hand.append(dli[j - 2])
                if players[op1i][i + 5] == ('h', j):
                    op1hand.append(hli[j - 2])
                if players[op2i][i + 5] == ('s', j):
                    op2hand.append(sli[j - 2])
                if players[op2i][i + 5] == ('c', j):
                    op2hand.append(cli[j - 2])
                if players[op2i][i + 5] == ('d', j):
                    op2hand.append(dli[j - 2])
                if players[op2i][i + 5] == ('h', j):
                    op2hand.append(hli[j - 2])
                if players[op3i][i + 5] == ('s', j):
                    op3hand.append(sli[j - 2])
                if players[op3i][i + 5] == ('c', j):
                    op3hand.append(cli[j - 2])
                if players[op3i][i + 5] == ('d', j):
                    op3hand.append(dli[j - 2])
                if players[op3i][i + 5] == ('h', j):
                    op3hand.append(hli[j - 2])
                if players[op4i][i + 5] == ('s', j):
                    op4hand.append(sli[j - 2])
                if players[op4i][i + 5] == ('c', j):
                    op4hand.append(cli[j - 2])
                if players[op4i][i + 5] == ('d', j):
                    op4hand.append(dli[j - 2])
                if players[op4i][i + 5] == ('h', j):
                    op4hand.append(hli[j - 2])
                if players[op5i][i + 5] == ('s', j):
                    op5hand.append(sli[j - 2])
                if players[op5i][i + 5] == ('c', j):
                    op5hand.append(cli[j - 2])
                if players[op5i][i + 5] == ('d', j):
                    op5hand.append(dli[j - 2])
                if players[op5i][i + 5] == ('h', j):
                    op5hand.append(hli[j - 2])
                if players[op6i][i + 5] == ('s', j):
                    op6hand.append(sli[j - 2])
                if players[op6i][i + 5] == ('c', j):
                    op6hand.append(cli[j - 2])
                if players[op6i][i + 5] == ('d', j):
                    op6hand.append(dli[j - 2])
                if players[op6i][i + 5] == ('h', j):
                    op6hand.append(hli[j - 2])
                if players[op7i][i + 5] == ('s', j):
                    op7hand.append(sli[j - 2])
                if players[op7i][i + 5] == ('c', j):
                    op7hand.append(cli[j - 2])
                if players[op7i][i + 5] == ('d', j):
                    op7hand.append(dli[j - 2])
                if players[op7i][i + 5] == ('h', j):
                    op7hand.append(hli[j - 2])
                if players[op8i][i + 5] == ('s', j):
                    op8hand.append(sli[j - 2])
                if players[op8i][i + 5] == ('c', j):
                    op8hand.append(cli[j - 2])
                if players[op8i][i + 5] == ('d', j):
                    op8hand.append(dli[j - 2])
                if players[op8i][i + 5] == ('h', j):
                    op8hand.append(hli[j - 2])
                if players[op9i][i + 5] == ('s', j):
                    op9hand.append(sli[j - 2])
                if players[op9i][i + 5] == ('c', j):
                    op9hand.append(cli[j - 2])
                if players[op9i][i + 5] == ('d', j):
                    op9hand.append(dli[j - 2])
                if players[op9i][i + 5] == ('h', j):
                    op9hand.append(hli[j - 2])
        pmoney = font.render(str(players[pi][1]), True, WHITE)
        ptable = font.render(str(table[pi]), True, WHITE)
        pname = font.render(str(players[pi][0]), True, WHITE)
        if players[pi][2] == 1:
            fold = "Playing"
            ppf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            ppf = font.render(fold, True, RED)
        if turn == 0 and pi == 7:
            screen.blit(db, (985, 610))
        if turn > 0 and pi == 9:
            screen.blit(db, (985, 610))
        screen.blit(pmoney, (980, 650))
        screen.blit(ppf, (980, 630))
        screen.blit(ptable, (860, 500))
        screen.blit(phand[0], (950, 670))
        screen.blit(phand[1], (1000, 670))
        screen.blit(pname, (980, 700))

        op1money = font.render(str(players[op1i][1]), True, WHITE)
        op1table = font.render(str(table[op1i]), True, WHITE)
        op1name = font.render(str(players[op1i][0]), True, WHITE)
        if players[op1i][2] == 1:
            fold = "Playing"
            op1pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op1pf = font.render(fold, True, RED)
        if turn == 0 and op1i == 7:
            screen.blit(db, (665, 610))
        if turn > 0 and op1i == 9:
            screen.blit(db, (665, 610))
        screen.blit(op1money, (660, 650))
        screen.blit(op1pf, (660, 630))
        screen.blit(op1table, (660, 500))
        screen.blit(back, (730, 600))
        screen.blit(back, (780, 600))
        if turn == 4 and players[op1i][2] == 1:
            screen.blit(op1hand[0], (730, 600))
            screen.blit(op1hand[1], (780, 600))
        screen.blit(op1name, (660, 700))

        op2money = font.render(str(players[op2i][1]), True, WHITE)
        op2table = font.render(str(table[op2i]), True, WHITE)
        op2hand1 = font.render(str(players[op2i][5]), True, WHITE)
        op2hand2 = font.render(str(players[op2i][6]), True, WHITE)
        op2name = font.render(str(players[op2i][0]), True, WHITE)
        if players[op2i][2] == 1:
            fold = "Playing"
            op2pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op2pf = font.render(fold, True, RED)
        if turn == 0 and op2i == 7:
            screen.blit(db, (355, 610))
        if turn > 0 and op2i == 9:
            screen.blit(db, (355, 610))
        screen.blit(op2money, (350, 650))
        screen.blit(op2pf, (350, 630))
        screen.blit(op2table, (350, 500))
        screen.blit(back, (430, 600))
        screen.blit(back, (480, 600))
        if turn == 4 and players[op2i][2] == 1:
            screen.blit(op2hand[0], (430, 600))
            screen.blit(op2hand[1], (480, 600))
        screen.blit(op2name, (350, 700))

        op3money = font.render(str(players[op3i][1]), True, WHITE)
        op3table = font.render(str(table[op3i]), True, WHITE)

        op3name = font.render(str(players[op3i][0]), True, WHITE)
        if players[op3i][2] == 1:
            fold = "Playing"
            op3pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op3pf = font.render(fold, True, RED)
        if turn == 0 and op3i == 7:
            screen.blit(db, (55, 610))
        if turn > 0 and op3i == 9:
            screen.blit(db, (55, 610))
        screen.blit(op3money, (50, 650))
        screen.blit(op3pf, (50, 630))
        screen.blit(op3table, (180, 500))
        screen.blit(back, (120, 600))
        screen.blit(back, (170, 600))
        if turn == 4 and players[op3i][2] == 1:
            screen.blit(op3hand[0], (120, 600))
            screen.blit(op3hand[1], (170, 600))
        screen.blit(op3name, (20, 700))

        op4money = font.render(str(players[op4i][1]), True, WHITE)
        op4table = font.render(str(table[op4i]), True, WHITE)
        op4name = font.render(str(players[op4i][0]), True, WHITE)
        if players[op4i][2] == 1:
            fold = "Playing"
            op4pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op4pf = font.render(fold, True, RED)
        if turn == 0 and op4i == 7:
            screen.blit(db, (80, 300))
        if turn > 0 and op4i == 9:
            screen.blit(db, (80, 300))
        screen.blit(op4money, (10, 320))
        screen.blit(op4pf, (10, 300))
        screen.blit(op4table, (180, 370))
        screen.blit(back, (10, 340))
        screen.blit(back, (60, 340))
        if turn == 4 and players[op4i][2] == 1:
            screen.blit(op4hand[0], (10, 340))
            screen.blit(op4hand[1], (60, 340))
        screen.blit(op4name, (10, 280))

        op5money = font.render(str(players[op5i][1]), True, WHITE)
        op5table = font.render(str(table[op5i]), True, WHITE)
        op5name = font.render(str(players[op5i][0]), True, WHITE)
        if players[op5i][2] == 1:
            fold = "Playing"
            op5pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op5pf = font.render(fold, True, RED)
        if turn == 0 and op5i == 7:
            screen.blit(db, (55, 120))
        if turn > 0 and op5i == 9:
            screen.blit(db, (55, 120))
        screen.blit(op5money, (50, 80))
        screen.blit(op5pf, (50, 100))
        screen.blit(op5table, (180, 250))
        screen.blit(back, (120, 10))
        screen.blit(back, (170, 10))
        if turn == 4 and players[op5i][2] == 1:
            screen.blit(op5hand[0], (120, 10))
            screen.blit(op5hand[1], (170, 10))
        screen.blit(op5name, (20, 20))

        op6money = font.render(str(players[op6i][1]), True, WHITE)
        op6table = font.render(str(table[op6i]), True, WHITE)
        op6name = font.render(str(players[op6i][0]), True, WHITE)
        if players[op6i][2] == 1:
            fold = "Playing"
            op6pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op6pf = font.render(fold, True, RED)
        if turn == 0 and op6i == 7:
            screen.blit(db, (355, 120))
        if turn > 0 and op6i == 9:
            screen.blit(db, (355, 120))
        screen.blit(op6money, (350, 80))
        screen.blit(op6pf, (350, 100))
        screen.blit(op6table, (350, 250))
        screen.blit(back, (430, 10))
        screen.blit(back, (480, 10))
        if turn == 4 and players[op6i][2] == 1:
            screen.blit(op6hand[0], (430, 10))
            screen.blit(op6hand[1], (480, 10))
        screen.blit(op6name, (350, 20))

        op7money = font.render(str(players[op7i][1]), True, WHITE)
        op7table = font.render(str(table[op7i]), True, WHITE)
        op7name = font.render(str(players[op7i][0]), True, WHITE)
        if players[op7i][2] == 1:
            fold = "Playing"
            op7pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op7pf = font.render(fold, True, RED)
        if turn == 0 and op7i == 7:
            screen.blit(db, (665, 120))
        if turn > 0 and op7i == 9:
            screen.blit(db, (665, 120))
        screen.blit(op7money, (660, 80))
        screen.blit(op7pf, (660, 100))
        screen.blit(op7table, (660, 250))
        screen.blit(back, (730, 10))
        screen.blit(back, (780, 10))
        if turn == 4 and players[op7i][2] == 1:
            screen.blit(op7hand[0], (730, 10))
            screen.blit(op7hand[1], (780, 10))
        screen.blit(op7name, (660, 20))

        op8money = font.render(str(players[op8i][1]), True, WHITE)
        op8table = font.render(str(table[op8i]), True, WHITE)
        op8name = font.render(str(players[op8i][0]), True, WHITE)
        if players[op8i][2] == 1:
            fold = "Playing"
            op8pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op8pf = font.render(fold, True, RED)
        if turn == 0 and op8i == 7:
            screen.blit(db, (1030, 210))
        if turn > 0 and op8i == 9:
            screen.blit(db, (1030, 210))
        screen.blit(op8money, (1030, 170))
        screen.blit(op8pf, (1030, 190))
        screen.blit(op8table, (860, 250))
        screen.blit(back, (950, 10))
        screen.blit(back, (1000, 10))
        if turn == 4 and players[op8i][2] == 1:
            screen.blit(op8hand[0], (950, 10))
            screen.blit(op8hand[1], (1000, 10))
        screen.blit(op8name, (1010, 140))

        op9money = font.render(str(players[op9i][1]), True, WHITE)
        op9table = font.render(str(table[op9i]), True, WHITE)
        op9name = font.render(str(players[op9i][0]), True, WHITE)
        if players[op9i][2] == 1:
            fold = "Playing"
            op9pf = font.render(fold, True, BLUE)
        else:
            fold = "Fold"
            op9pf = font.render(fold, True, RED)
        if turn == 0 and op9i == 7:
            screen.blit(db, (975, 300))
        if turn > 0 and op9i == 9:
            screen.blit(db, (975, 300))
        screen.blit(op9money, (1030, 320))
        screen.blit(op9pf, (1030, 300))
        screen.blit(op9table, (860, 370))
        screen.blit(back, (950, 340))
        screen.blit(back, (1000, 340))
        if turn == 4 and players[op9i][2] == 1:
            screen.blit(op9hand[0], (950, 340))
            screen.blit(op9hand[1], (1000, 340))
        screen.blit(op9name, (1010, 280))

    pg.display.flip()

    if turn == 4:
        pg.time.wait(2000)

def betting():  ##베팅 함수
    global fold
    global lowlimit
    global nowplay
    nowplay = None
    i = 0
    calls = 0  ##콜 한 횟수(플레이어 수 만큼 모여야 다음으로 넘어감)
    someonebet = []  # 이거의 마지막 값만 보면 됨. someonebet[-1] 이 현재 걸려있는 베팅금액
    while 1:
        i = i % len(players)
        nowplay = i % len(players)
        Prefresh0(table, turn, pot, nowplay)
        if players[i][2] != 0:
            pg.time.wait(3000)
        while 1:
            act = None
            if players[i][2] == 0:
                calls += 1
                break
            # print('max(table)', max(table))
            if table[i] != max(table) and max(table) < 2000:  # 2000이거나 아니거나에서 2000미만이거나 2000이상으로 조건을 바꿈
                if players[i][0] == 'player':
                    # print('player HAND, MONEY: ', players[i][5], players[i][6], players[i][1])
                    for e in pg.event.get():
                        if e.type == pg.KEYDOWN:
                            if e.key == pg.K_UP:
                                act = 3
                                print("up")
                            elif e.key == pg.K_RIGHT:
                                act = 2
                                print("r")
                            elif e.key == pg.K_DOWN:
                                act = 1
                                print("d")
                else:
                    aipt = players[i][4].aipoint(comcard, players[i][5], players[i][6])
                    act = players[i][4].turnaction(turn, aipt, someonebet, players[i][5], players[i][6])  # AI행동, 가능성 기반
                Prefresh0(table, turn, pot, nowplay)
            elif table[i] == max(table) and max(table) < 2000:
                if players[i][0] == 'player':
                    # print('player HAND, MONEY: ', players[i][5], players[i][6], players[i][1])
                    for e in pg.event.get():
                        if e.type == pg.KEYDOWN:
                            if e.key == pg.K_UP:
                                act = 3
                                print("up")
                            elif e.key == pg.K_RIGHT:
                                act = 2
                                print("r")
                            elif e.key == pg.K_DOWN:
                                act = 1
                                print("d")
                else:  # AI의 함수호출
                    aipt = players[i][4].aipoint(comcard, players[i][5], players[i][6])
                    act = players[i][4].turnaction(turn, aipt, someonebet, players[i][5], players[i][6])  # AI행동, 가능성 기반
                Prefresh0(table, turn, pot, nowplay)
            elif table[i] != max(table) and max(table) >= 2000:
                while 1:  ####################################수정된 코드5월 2일#####################################
                    if players[i][0] == 'player':
                        # print('player HAND, MONEY: ', players[i][5], players[i][6], players[i][1])
                        for e in pg.event.get():
                            if e.type == pg.KEYDOWN:
                                if e.key == pg.K_RIGHT:
                                    act = 2
                                    print("r")
                                elif e.key == pg.K_DOWN:
                                    act = 1
                                    print("d")
                    else:
                        aipt = players[i][4].aipoint(comcard, players[i][5], players[i][6])
                        act = players[i][4].turnaction(turn, aipt, someonebet, players[i][5],
                                                       players[i][6])  # AI행동, 가능성 기반
                    Prefresh0(table, turn, pot, nowplay)
                    if act == 1 or act == 2 or act == 0:
                        break


            if act == 1:
                print('Fold')
                players[i][2] = 0
                calls += 1
                fold += 1
            elif act == 2:
                if table[i] != max(table):
                    print('콜합니다')
                    players[i][1] -= max(table) - table[i]
                    table[i] += max(table) - table[i]  # 남들이 베팅한 금액에 맞춰 베팅
                else:
                    print('체크합니다')
                calls += 1
            elif act == 3:
                if lowlimit < 2000:
                    if players[i][0] == 'player':
                        # 입력버튼자리
                        font = pg.font.Font(None, 50)  # 폰트 설정
                        screen.fill(BLACK)
                        line1 = font.render((' Type your bet.'), True, WHITE)
                        line2 = font.render((' Minimum %d Maximum 2000 ' % lowlimit), True, WHITE)
                        screen.blit(line1, (400, 250))
                        screen.blit(line2, (300, 350))
                        pg.display.flip()
                        text = ''
                        bet = 0
                        while 1:
                            for e in pg.event.get():
                                if e.type == pg.KEYDOWN:
                                    if e.key == pg.K_RETURN:
                                        bet = text
                                        bet = int(bet)
                                        text = ''
                                        break
                                    elif e.key == pg.K_BACKSPACE:
                                        screen.fill(BLACK)
                                        text = text[:-1]
                                    else:
                                        screen.fill(BLACK)
                                        text += e.unicode
                            if lowlimit <= bet <= 2000:
                                break
                            block = font.render(text, True, WHITE)
                            rect = block.get_rect()
                            rect.center = screen.get_rect().center
                            screen.blit(block, rect)
                            pg.display.flip()
                        Prefresh0(table, turn, pot, nowplay)
                        pg.time.wait(2000)



                    else:  # AI 베팅
                        print(players[i][0] + " raise!")
                        aipt = players[i][4].aipoint(comcard, players[i][5], players[i][6])  # @@@@@@@@@@@@@@@@@@@@@@@@
                        bet = players[i][4].bet(lowlimit, 2000, aipt, players[i][5], players[i][6])
                        print(bet)
                    if lowlimit <= bet <= 2000:
                        players[i][1] -= bet
                        table[i] += bet
                        calls = 1
                        lowlimit = bet * 2
                    else:
                        print('다시 입력해 주십시오')
                        continue
                elif 2000 <= lowlimit:
                    if players[i][0] == 'player':
                        # 입력버튼자리
                        font = pg.font.Font(None, 50)  # 폰트 설정
                        screen.fill(BLACK)
                        line1 = font.render((' Type your bet.'), True, WHITE)
                        line2 = font.render((' Type 2000 '), True, WHITE)
                        screen.blit(line1, (400, 250))
                        screen.blit(line2, (400, 350))
                        pg.display.flip()
                        text = ''
                        bet = 0
                        while 1:
                            for e in pg.event.get():
                                if e.type == pg.KEYDOWN:
                                    if e.key == pg.K_RETURN:
                                        bet = text
                                        bet = int(bet)
                                        text = ''
                                        break
                                    elif e.key == pg.K_BACKSPACE:
                                        screen.fill(BLACK)
                                        text = text[:-1]
                                    else:
                                        screen.fill(BLACK)
                                        text += e.unicode
                            if bet == 2000:
                                break
                            block = font.render(text, True, WHITE)
                            rect = block.get_rect()
                            rect.center = screen.get_rect().center
                            screen.blit(block, rect)
                            pg.display.flip()
                        Prefresh0(table, turn, pot, nowplay)
                    else:  # AI베팅
                        print(players[i][0] + "raise:")
                        aipt = players[i][4].aipoint(comcard, players[i][5], players[i][6])  # @@@@@@@@@@@@@@@@@@@@@@@@
                        bet = players[i][4].bet(lowlimit, 2000, aipt, players[i][5], players[i][6])
                        print(bet)
                    if bet == 2000:
                        players[i][1] -= bet
                        table[i] += bet
                        calls = 1
                        lowlimit = bet * 2
                    else:
                        print('다시 입력해 주십시오')
                        continue
                elif lowlimit == 4000:
                    continue
                someonebet.append(bet)
            elif act == 0:
                print(players[i])
                print(pot)
                print(table)
                print(comcard)
                continue
            elif act == 9:
                print(deck)
                print(len(deck))
            else:
                continue
            break
        i += 1
        if fold == opnum:
            break
        if calls == len(players):
            break
        Prefresh0(table, turn, pot, nowplay)


def tabletopot():  ##테이블->팟으로 돈 이동
    global pot
    for i in range(len(table)):
        pot += table[i]
        table[i] = 0


def nodecision():
    global pot
    global fold
    print('무승부입니다. 판돈을 나눠갖습니다.')
    c = 0
    for i in range(len(players)):
        if players[i][2] == 44:
            c += 1
    for i in range(len(players)):
        if players[i][2] == 44:
            players[i][1] += pot / c


def showdown():
    print('\n------------------------쇼다운------------------------\n')
    global pot

    score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  ##쇼다운의 결과 점수만 모아놓은 리스트
    maxnum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  ##쇼다운의 결과 카드 번호만 모아놓은 리스트
    maxlist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  ## 쇼다운의 결과 같은번호의 카드 갯수를 모아놓은 리스트
    maxindex = []
    straightnum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  ##스트레이트 승자판정용 리스트

    flushcard = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    comli = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Prefresh0(table, turn, pot, nowplay)
    for i in range(len(players)):
        if players[i][2] == 0:
            continue
        else:
            cards = []  ##결과물을 조합할 리스트
            cards.append(players[i][5])
            cards.append(players[i][6])
            cards += comcard

            straight = 0
            flush = 0

            num = [cards[j][1] for j in range(7)]
            num.sort()
            maxnum[i] = num

            suit = [cards[j][0] for j in range(7)]
            suit.sort()

            li = [num.count(j) for j in range(2, 15)]
            maxlist[i] = li

            if 4 in li:#4cards
                players[i][3] = 8
            elif 3 in li and 2 in li:#fullhouse
                players[i][3] = 7
            elif 3 in li and 2 not in li:#3cards
                players[i][3] = 4
            elif li.count(2) == 2 or li.count(2) == 3:#2pair
                players[i][3] = 3
            elif li.count(2) == 1:#onepair
                players[i][3] = 2
            elif li.count(1) == 7:#highcard
                players[i][3] = 1

            if suit.count('s') >= 5 or suit.count('h') >= 5 or suit.count('c') >= 5 or suit.count('d') >= 5:
                fli = []
                for j in range(len(cards)):
                    if suit.count('s') >= 5:
                        if cards[j][0] == 's':
                            fli.append(cards[j][1])
                    elif suit.count('h') >= 5:
                        if cards[j][0] == 'h':
                            fli.append(cards[j][1])
                    elif suit.count('c') >= 5:
                        if cards[j][0] == 'c':
                            fli.append(cards[j][1])
                    elif suit.count('d') >= 5:
                        if cards[j][0] == 'd':
                            fli.append(cards[j][1])
                fli.sort()
                fli.reverse()
                del fli[5:]
                flushcard[i] = fli
                flush = 1
                if players[i][3] < 6:
                    players[i][3] = 6

            if li[12] > 0 and li[11] > 0 and li[10] > 0 and li[9] > 0 and li[8] > 0:
                straight = 2
            elif li[12] > 0 and li[0] > 0 and li[1] > 0 and li[2] > 0 and li[3] > 0:
                straight = 1
                straightnum[i] = li[3]
            else:
                for j in range(3):
                    if num[6 - j] - num[2 - j] == 4 and len(set(num[2 - j:7 - j])) == 5:
                        straight = 1
                        straightnum[i] = num[6 - j]

            if straight == 2 and flush == 1:
                players[i][3] = 10
            elif flushcard[i] != 0 and flushcard[i][4] - flushcard[i][0] == 4:
                players[i][3] = 9
            elif straight == 1:
                players[i][3] == 5

            score[i] = players[i][3]

    # print(players)

    for i in range(len(players)):
        li = []
        if players[i][3] == max(score) and score.count(max(score)) == 1:
            players[i][2] = 99
        elif players[i][3] == max(score) and score.count(max(score)) != 1:
            if players[i][3] == 10:
                comli[i] = 44
            elif players[i][3] == 9:
                li.append(straightnum[i])
                comli[i] = li
            elif players[i][3] == 8:
                li.append(maxlist.index(4))
                while 1:
                    a = maxlist[i].pop()
                    if a != 0 and a != 4:
                        li.append(len(maxlist[i]))
                        break
                comli[i] = li
            elif players[i][3] == 7:
                while 1:
                    print(maxlist, i)
                    a = maxlist[i].pop()
                    if a == 3:
                        li.append(len(maxlist[i]))
                        break
                if 3 in maxlist[i]:
                    li.append(maxlist[i].index(3))
                else:
                    while 1:
                        a = maxlist[i].pop()
                        if a == 2:
                            li.append(len(maxlist[i]))
                            break
                comli[i] = li
            elif players[i][3] == 6:
                comli[i] = flushcard[i][0:5]
            elif players[i][3] == 5:
                li.append(straightnum[i])
                comli[i] = li
            elif players[i][3] == 4:
                li.append(maxlist[i].index(3))
                c = 0
                while 1:
                    a = maxlist[i].pop()
                    if a == 1:
                        li.append(len(maxlist[i]))
                        c += 1
                    if c == 2:
                        break
                comli[i] = li
            elif players[i][3] == 3:
                for j in range(2):
                    li.append(maxlist[i].index(2))
                    maxlist[i][maxlist[i].index(2)] = 0
                while 1:
                    a = maxlist[i].pop()
                    if a == 1:
                        li.append(len(maxlist[i]))
                        break
                comli[i] = li
            elif players[i][3] == 2:
                li.append(maxlist[i].index(2))
                c = 0
                while 1:
                    a = maxlist[i].pop()
                    if a == 1:
                        li.append(len(maxlist[i]))
                        c += 1
                    if c == 3:
                        break
                comli[i] = li
            elif players[i][3] == 1:
                c = 0
                while 1:
                    a = maxlist[i].pop()
                    if a == 1:
                        li.append(len(maxlist[i]))
                        c += 1
                    if c == 5:
                        break
                comli[i] = li

    for i in range(len(comli)):
        if comli[i] != 0:
            a = len(comli[i])

    # print(comli)
    if comli.count(0) < 4:
        for k in range(a):
            if comli.count(0) == 4:
                break
            prime = 0
            li = []
            for i in range(len(comli)):
                if comli[i] != 0 and comli[i] != 44:
                    li.append(comli[i][k])
            prime = max(li)
            for i in range(len(comli)):
                if comli[i] != 0 and comli[i] != 44:
                    if comli[i][k] < prime:
                        comli[i] = 0

    if comli.count(0) < 4:
        for i in range(len(comli)):
            if comli[i] != 0:
                comli[i] = 44

    for i in range(len(comli)):
        if comli[i] == 44:
            nodecision()
            comli = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            break

    # print(comli)

    for i in range(len(comli)):
        if comli[i] != 0:
            players[i][2] = 99
    pg.time.wait(2000)
    font = pg.font.Font(None, 50)  # 폰트 설정
    screen.fill(BLACK)
    # print(players)
    for i in range(len(players)):
        if players[i][2] == 99:
            if players[i][3] == 10:
                line1 = font.render(('%s Wins with Royal Flush!' % players[i][0]), True, WHITE)
                print('%s가 Royal Flush로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 9:
                line1 = font.render(('%s Wins with Straight Flush!' % players[i][0]), True, WHITE)
                print('%s가Straight Flush로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 8:
                line1 = font.render(('%s Wins with Four of a Kind!' % players[i][0]), True, WHITE)
                print('%s가 Four of a Kind로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 7:
                line1 = font.render(('%s Wins with Full House!' % players[i][0]), True, WHITE)
                print('%s가 Full House로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 6:
                line1 = font.render(('%s Wins with Flush!' % players[i][0]), True, WHITE)
                print('%s가 Flush로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 5:
                line1 = font.render(('%s Wins with Straight!' % players[i][0]), True, WHITE)
                print('%s가 Straight로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 4:
                line1 = font.render(('%s Wins with Three of a Kind!' % players[i][0]), True, WHITE)
                print('%s가 Three of a Kind로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 3:
                line1 = font.render(('%s Wins with Two Pair!' % players[i][0]), True, WHITE)
                print('%s가 Two Pair로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 2:
                line1 = font.render(('%s Wins with One Pair!' % players[i][0]), True, WHITE)
                print('%s가 One Pair로 승리하였습니다!\n' % players[i][0])
            elif players[i][3] == 1:
                line1 = font.render(('%s Wins with High Card!' % players[i][0]), True, WHITE)
                print('%s가 High Card로 승리하였습니다!\n' % players[i][0])
            screen.blit(line1, (280, 250))
            pg.display.flip()
            pg.time.wait(2000)
            players[i][1] += pot
            pot = 0


def balancecheck():  ##5.13추가
    for i in range(len(players)):
        if players[i][1] < 2000:
            if i == 0:
                font = pg.font.Font(None, 50)  # 폰트 설정
                screen.fill(BLACK)
                line1 = font.render(("You've exhausted all the money"), True, WHITE)
                line2 = font.render(('You decided to go home'), True, WHITE)
                screen.blit(line1, (480, 250))
                screen.blit(line2, (500, 350))
                pg.display.flip()
                pg.time.wait(2000)
                sys.exit()
            else:
                font = pg.font.Font(None, 50)  # 폰트 설정
                screen.fill(BLACK)
                line1 = font.render(("%s've exhausted all the money" % players[i][0]), True, WHITE)
                line2 = font.render(('He decided to go home'), True, WHITE)
                screen.blit(line1, (460, 250))
                screen.blit(line2, (500, 350))
                pg.display.flip()
                pg.time.wait(2000)
                del players[i]


##AI클래스@@@@@@@@@@@@
class AIplayer:
    fold = 0

    def name(self, name):
        self.name = name
        return self.name

    def aipoint(self, comcard, hand1, hand2):  # 컴퓨터가 자신의 핸드 + 커뮤니티 족보를 판단
        flush = 0
        threeKind = 0
        fourKind = 0
        pairCount = 0
        full = 0

        handset = [hand1, hand2]
        cardset = comcard[:] + handset[:]
        cards = cardset
        cards.sort(key=lambda x: -x[1])  # 두번째 튜플로 내림차순 정렬
        alphacards = [x[0] for x in cards]  # 알파벳 모음
        numcards = []
        for i in cards:
            numcards.append(i[1])

        if alphacards.count('s') == 5 or alphacards.count('d') == 5 or alphacards.count('h') == 5 or alphacards.count(
                'c') == 5:  # 무늬가 5장 같을 경우 ( 플러쉬)
            flush = 1

        for i in range(2, 15):
            if numcards.count(i) == 4:  # 포카드
                fourKind = 1
            elif numcards.count(i) == 3:  # 쓰리카드
                threeKind = 1
            elif numcards.count(i) == 2:  # 페어
                pairCount += 1

        if threeKind and pairCount:
            full = 1  # 풀하우스

        if len(cards) >= 5:
            for i in range(0, len(cards) - 4):  # 스트레이트 (5장의 카드가 연속)
                if numcards[i] - 1 == numcards[i + 1] and numcards[i + 1] - 1 == numcards[i + 2] and numcards[
                    i + 2] - 1 == numcards[i + 3] and numcards[i + 3] - 1 == numcards[i + 4]:
                    if alphacards[i] == alphacards[i + 1] == alphacards[i + 2] == alphacards[i + 3] == alphacards[
                        i + 4]:  # 스트레이트인 카드들의 무늬가 같음
                        if numcards[0] == 14:  # 무늬가 같은데 가장 큰 숫자가 14
                            # print('로열플러쉬!')
                            return 10
                        # print('스트레이트 플러쉬!')
                        return 9
                    # print('스트레이트!')
                    return 5

        if fourKind == 1:
            return 8  # 포카드

        elif full == 1:
            return 7  # 풀하우스

        elif flush == 1:
            return 6  # 플러쉬

        elif threeKind == 1:
            return 4  # 트리플

        elif pairCount >= 2:
            return 3  # 투페어

        elif pairCount == 1:
            return 2  # 원페어

        else:
            return 0.1 * numcards[0]  # 하이카드

    def turnaction(self, turn, aipt, someonebet, hand1, hand2):  # 턴 별 액션
        mybet = 1000
        mybt = round(mybet * (1 + 0.1 * aipt))
        print(self.name + ":")
        if turn == 0:  # turn0 일때 핸드체크
            if self.hand_check(hand1, hand2) == 'premium' or self.hand_check(hand1,
                                                                             hand2) == 'special' or self.hand_check(
                    hand1, hand2) == 'good':
                if someonebet:  # 누군가의 베팅이 존재한다면
                    if someonebet[-1] == 2000:  # 그리고 누군가의 마지막 베팅이 2000이라면
                        return 2  # 콜하고 끝
                return 3
            elif self.hand_check(hand1, hand2) == 'fold':
                return 1


        elif turn >= 1:
            if someonebet:
                if mybt > someonebet[-1]:
                    if 2000 in someonebet and aipt >= 3:
                        return 2
                    return 3
                elif mybt == someonebet[-1]:
                    return 2
                else:
                    if 2000 in someonebet and aipt >= 3:
                        return 2
                    return 1

            else:
                if aipt >= 1:
                    return 3

                elif aipt < 1:
                    return 2

    def bet(self, lowlimit, maxlimit, aipt, hand1, hand2):  # 베팅함수
        upbet = 1000
        ten = random.randint(0, 100)
        if lowlimit * 2 >= 2000:
            aibet = 2000
        else:
            if aipt >= 2:
                aibet = round(upbet * (1 + 0.1 * aipt)) + ten
            else:
                highcard = max(hand1[1], hand2[1])
                aibet = round(upbet * (0.1 * highcard)) + ten
            if aibet >= 2000:
                aibet = 2000
        return aibet

    def showhand(self):  # 패공개
        return 1

    def hand_check(self, hand1, hand2):  # 핸드체크, 프레플랍 단계 먼저 자신에게 주어진 카드 정보를 분석한다.
        premium = [('p', 14, 14), ('p', 13, 13), ('p', 12, 12), ('s', 14, 13), ('p', 11, 11), ('s', 14, 12),
                   ('s', 13, 12), ('s', 14, 11), ('s', 13, 11), ('p', 10, 10), ('o', 14, 13), ('s', 14, 10),
                   ('s', 12, 11), ('s', 13, 10), ('s', 12, 10), ('s', 11, 10), ('p', 9, 9)]
        special = [('o', 14, 12), ('s', 14, 9), ('o', 13, 12), ('p', 8, 8), ('s', 13, 9), ('s', 10, 9), ('s', 14, 8),
                   ('s', 12, 9), ('s', 11, 9), ('o', 14, 11), ('s', 14, 5), ('p', 7, 7), ('s', 14, 7), ('o', 13, 11),
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

        if premium.count(tup) == 1:
            return ('premium')
        elif special.count(tup) == 1:
            return ('special')
        elif good.count(tup) == 1:  # 판단
            return ('good')
        else:
            return ('fold')


pg.init()
size = [1080, 720]
screen = pg.display.set_mode(size)
pg.display.set_caption("Game Title")
gameend = False
clock= pg.time.Clock()
BLACK= ( 50,  50,  50)
WHITE= (255,255,255)
BLUE = ( 70,  93, 194)
GREEN= ( 0,255,  0)
RED  = (209,  55,  37)
validChars = "1234567890"
textBox0 = TextBox0()
textBox1 = TextBox1()
textBox2 = TextBox2()
textBox0.rect.center = [540, 360]
textBox1.rect.center = [540, 360]
textBox2.rect.center = [540, 360]
h2 = pg.image.load("h2.jpg")
h3 = pg.image.load("h3.jpg")
h4 = pg.image.load("h4.jpg")
h5 = pg.image.load("h5.jpg")
h6 = pg.image.load("h6.jpg")
h7 = pg.image.load("h7.jpg")
h8 = pg.image.load("h8.jpg")
h9 = pg.image.load("h9.jpg")
h10 = pg.image.load("h10.jpg")
h11 = pg.image.load("h11.jpg")
h12 = pg.image.load("h12.jpg")
h13 = pg.image.load("h13.jpg")
h14 = pg.image.load("h14.jpg")
hli = [h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12, h13, h14]
s2 = pg.image.load("s2.jpg")
s3 = pg.image.load("s3.jpg")
s4 = pg.image.load("s4.jpg")
s5 = pg.image.load("s5.jpg")
s6 = pg.image.load("s6.jpg")
s7 = pg.image.load("s7.jpg")
s8 = pg.image.load("s8.jpg")
s9 = pg.image.load("s9.jpg")
s10 = pg.image.load("s10.jpg")
s11 = pg.image.load("s11.jpg")
s12 = pg.image.load("s12.jpg")
s13 = pg.image.load("s13.jpg")
s14 = pg.image.load("s14.jpg")
sli = [s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14]
d2 = pg.image.load("d2.jpg")
d3 = pg.image.load("d3.jpg")
d4 = pg.image.load("d4.jpg")
d5 = pg.image.load("d5.jpg")
d6 = pg.image.load("d6.jpg")
d7 = pg.image.load("d7.jpg")
d8 = pg.image.load("d8.jpg")
d9 = pg.image.load("d9.jpg")
d10 = pg.image.load("d10.jpg")
d11 = pg.image.load("d11.jpg")
d12 = pg.image.load("d12.jpg")
d13 = pg.image.load("d13.jpg")
d14 = pg.image.load("d14.jpg")
dli = [d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14]
c2 = pg.image.load("c2.jpg")
c3 = pg.image.load("c3.jpg")
c4 = pg.image.load("c4.jpg")
c5 = pg.image.load("c5.jpg")
c6 = pg.image.load("c6.jpg")
c7 = pg.image.load("c7.jpg")
c8 = pg.image.load("c8.jpg")
c9 = pg.image.load("c9.jpg")
c10 = pg.image.load("c10.jpg")
c11 = pg.image.load("c11.jpg")
c12 = pg.image.load("c12.jpg")
c13 = pg.image.load("c13.jpg")
c14 = pg.image.load("c14.jpg")
cli = [c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14]
back = pg.image.load("back.jpg")
while not gameend:
    clock.tick(30)
    screen.fill(WHITE)
    screen.blit(textBox0.image, textBox0.rect)
    pg.display.flip()
    while 1:
        for e in pg.event.get():
            if e.type == pg.KEYDOWN:
                textBox0.add_chr(pg.key.name(e.key))
                if e.key == pg.K_RETURN:
                    if len(textBox0.text) > 0:
                        print(textBox0.text)
        screen.blit(textBox0.image, textBox0.rect)
        pg.display.flip()
        if textBox0.text != '':
            break
    print(textBox0.text)
    modsel = int(textBox0.text)
    if modsel == 1:
        screen.fill(WHITE)
        pg.display.flip()
        while 1:
            for e in pg.event.get():
                if e.type == pg.KEYDOWN:
                    textBox1.add_chr(pg.key.name(e.key))
                    if e.key == pg.K_RETURN:
                        if len(textBox1.text) > 0:
                            print(textBox1.text)
            screen.blit(textBox1.image, textBox1.rect)
            pg.display.flip()
            if textBox1.text != '':
                break
        font = pg.font.Font(None, 50)  # 폰트 설정
        screen.fill(BLACK)
        line1 = font.render('How to play', True, WHITE)
        line2 = font.render('Press the KEY', True, WHITE)
        line3 = font.render('UP KEY = Raise', True, WHITE)
        line4 = font.render('DOWN KEY = Fold', True, WHITE)
        line5 = font.render('RIGHT KEY = Call', True, WHITE)
        screen.blit(line1, (400, 100))
        screen.blit(line2, (400, 200))
        screen.blit(line3, (400, 300))
        screen.blit(line4, (400, 400))
        screen.blit(line5, (400, 500))
        pg.display.flip()
        pg.time.wait(3000)
        screen.fill(BLACK)
        pg.display.flip()

        player = ['player', 50000, 1, 0, '주소']  ##플레이어 초기화, 50000은 자본금, 1은 폴드가 아님을 표시, 0은 승패용 점수
        ##주소는 객체만 필요하지만 인덱스 수를 맞추기 위해 추가
        players = [player]
        opnum = int(textBox1.text)
        for i in range(1, opnum + 1):
            globals()['opponent{}'.format(i)] = [str('opponent{}'.format(i)), 50000, 1, 0,
                                                 '주소']  ##opponent1, 2, 3과 같은 이름으로 상대방 초기화, 객체주소위치
            players.append(globals()['opponent{}'.format(i)])

            ##객체생성@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        for i in range(1, opnum + 1):
            name = players[i][0]
            players[i][4] = AIplayer()
            players[i][4].name(name)  # 이름 저장

        count = 0  ##게임 횟수

        while 1:
            screen.fill(BLACK)
            pg.display.flip()
            fold = 0  # 포기한 사람의 수
            turn = 0
            comcard = []  # 공용패
            pot = 0  ##확정 판돈
            table = []  # 베팅금 임시보관

            balancecheck()  # 5.13추가

            for i in range(len(players)):
                table.append(0)
            count += 1
            deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
            random.shuffle(deck)

            if len(players) > 2:
                print('\n딜러버튼은 %s입니다. %s가 스몰블라인드, %s가 빅블라인드 지불합니다.' % (players[0][0], players[1][0], players[2][0]))
                players[1][1] -= 100
                table[1] += 100
                players[2][1] -= 200
                table[2] += 200
            else:
                print('\n딜러버튼은 %s입니다. %s가 블라인드 지불합니다.' % (players[0][0], players[1][0]))
                players[1][1] -= 200
                table[1] += 200
            players.append(players[0])
            del players[0]
            table.append(table[0])
            del table[0]
            for i in range(len(players) * 2):  ##각각의 플레이어가 [이름, 자본금, 폴드여부, (카드1), (카드2)]의 모양으로 손패를 가지게 됨
                players[i % len(players)].append(deck.pop())
            if len(players) > 2:  ##플레이어 숫자에에 따라 순서 정하기
                for i in range(2):
                    players.append(players[0])
                    del players[0]
                    table.append(table[0])
                    del table[0]
            else:
                players.append(players[0])
                del players[0]
                table.append(table[0])
                del table[0]
                # print(table)

            while 1:
                # print(players)
                turns = ['Pre-flop', 'Flop', 'Turn', 'River(Last turn)']

                print('---------------------- %s ----------------------\n' % turns[turn])
                if turn == 0:
                    lowlimit = 400
                else:
                    lowlimit = 200
                betting()
                tabletopot()
                print(players)
                print(fold)
                if fold == opnum:  ##1명 빼고 모두가 폴드한 경우
                    for i in range(len(players)):
                        if players[i][2] == 1:
                            tabletopot()
                            players[i][1] += pot
                            pot = 0
                            font = pg.font.Font(None, 50)  # 폰트 설정
                            screen.fill(BLACK)
                            line1 = font.render(('Winner is %s ' % players[i][0]), True, WHITE)
                            line2 = font.render(('other players folded'), True, WHITE)
                            screen.blit(line1, (300, 250))
                            screen.blit(line2, (500, 350))
                            pg.display.flip()
                            pg.time.wait(2000)

                            if turn == 0:
                                turnmove(turn)
                    break
                turn += 1
                if turn == 1:
                    for i in range(3):  ##카드 3장 깔기
                        comcard.append(deck.pop())
                    turnmove(turn)
                elif turn < 4:  ##턴이 2, 3 일때 카드 1장씩 깔기
                    comcard.append(deck.pop())
                elif turn == 4:  # 쇼다운으로 넘어감
                    showdown()
                    break
                print('\nCommunity Cards: ', comcard)
            for i in range(len(players)):
                players[i][2] = 1  ##폴드한 사람들 부활
                del players[i][5:7]  ##손패 초기화
                players[i][3] = 0  ##점수초기화'''
    elif modsel == 2:
        screen.fill(WHITE)
        pg.display.flip()
        while 1:
            for e in pg.event.get():
                if e.type == pg.KEYDOWN:
                    textBox2.add_chr(pg.key.name(e.key))
                    if e.key == pg.K_RETURN:
                        if len(textBox2.text) > 0:
                            print(textBox2.text)
            screen.blit(textBox2.image, textBox2.rect)
            pg.display.flip()
            if textBox2.text != '':
                break
        opsel = int(textBox2.text)
        #p1 = Monte_Carlo_player()
        #p1 = Random_player()
        p1 = Human_player()
        if opsel == 1:
            p2 = Random_player()
        elif opsel == 2:
            p2 = Monte_Carlo_player()
        screen.fill(BLACK)
        font = pg.font.Font(None, 50)
        line1 = font.render('How to play', True, WHITE)
        line2 = font.render('UP KEY = Raise', True, WHITE)
        line3 = font.render('DOWN KEY = Fold', True, WHITE)
        line4 = font.render('RIGHT KEY = Call', True, WHITE)
        screen.blit(line1, (420, 150))
        screen.blit(line2, (390, 300))
        screen.blit(line3, (380, 400))
        screen.blit(line4, (380, 500))
        pg.display.flip()
        pg.time.wait(3000)
        screen.fill(BLACK)
        pg.display.flip()
        screen.fill(BLACK)
        pg.display.flip()
        #p1 = Monte_Carlo_player()
        #p1 = Random_player()
        #p1 = Human_player()
        #p2 = Random_player()
        #p2 = Monte_Carlo_player()
        #p2 = Human_player()
        prt = Printer()
        # 지정된 게임 수를 자동으로 두게 할 것인지 한 게임씩 두게 할 것인지 결정
        # auto = True : 지정된 판 수 (games)를 자동으로 진행
        # auto = Flase: 한 게임씩 진행
        auto = True

        #auto 모드의 게임 수
        games = 1100

        #각 플레이어의 승리 횟수를 저장
        p1_score = 0
        p2_score = 0
        draw_score = 0

        start = time.time()
        if auto:

            # 자동모드 실행
            for j in range(games):
                np.random.seed(j)
                env = Environment()
                p1.hand1, p1.hand2 = env.deck.pop(), env.deck.pop()
                p2.hand1, p2.hand2 = env.deck.pop(), env.deck.pop()

                Prefresh1()
                print(
                    '\n------------------------------------------------------------------------------------------------------------------')
                print("p1 player, money, hand : {} {} {}{}".format(p1.name, p1.bal, p1.hand1, p1.hand2))
                print("p2 player, money hand: {} {} {}{}".format(p2.name, p2.bal, p2.hand1, p2.hand2))

                if (p1.bal < 0) or (p2.bal < 0):
                    print('Player Balance Under 0, End this Game.\n')
                    break
                for i in range(10000):
                    sum = p1.bal + p2.bal

                    reward, done = env.move(p1, p2)  # ,(-1)**i)
                    print('각자 베팅', env.bet1, env.bet2)
                    print('reward, done', reward, done)
                    print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal + p2.bal))
                    print('after move', sum, env.bet1, env.bet2)
                    '''if sum != 100000:
                        print('after move', sum, env.bet1, env.bet2)
                        input()'''

                    # prt.round_info(p1,p2,env) # 라운드 수행결과 프린트
                    # 게임 종료 체크
                    global open
                    open = 1
                    Prefresh1()
                    screen.fill(BLACK)
                    font = pg.font.Font(None, 50)
                    if done == True:
                        if reward == 1:
                            print("j = {} winner is p1({})".format(j, p1.name))
                            p1_score += 1
                            line1 = font.render('Round{}'.format(j), True, WHITE)
                            line2 = font.render('Winner is player', True, WHITE)
                            screen.blit(line1, (420, 150))
                            screen.blit(line2, (390, 300))
                        elif reward == -1:
                            print("j = {} winner is p2({})".format(j, p2.name))
                            p2_score += 1
                            line1 = font.render('Round{}'.format(j), True, WHITE)
                            line2 = font.render('Winner is {}'.format(p2.name), True, WHITE)
                            screen.blit(line1, (420, 150))
                            screen.blit(line2, (390, 300))
                        else:
                            print("j = {} winner is draw".format(j))
                            draw_score += 1
                            line1 = font.render('Round{}'.format(j), True, WHITE)
                            line2 = font.render('No Winner', True, WHITE)
                            screen.blit(line1, (420, 150))
                            screen.blit(line2, (390, 300))
                        pg.display.flip()
                        pg.time.wait(3000)
                        screen.fill(BLACK)
                        break
            print("Good Game!")
            print(
                "\n현재 라운드: {}\n{} 승리 횟수: {} {} 승리 횟수: {} 비긴 횟수: {}".format(j, p1.name, p1_score, p2.name, p2_score, draw_score))
            print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal + p2.bal))
            game_time = time.time() - start
            print("수행 시간: {}".format(game_time))
            prt.after_round(game_time, p1, p2, p1_score, p2_score, draw_score, j)
            gameend = True
        else:
            # 한 게임씩 진행하는 수동 모드
            while True:
                # env = Environment()
                env = Environment()
                p1.hand1, p1.hand2 = env.deck.pop(), env.deck.pop()
                p2.hand1, p2.hand2 = env.deck.pop(), env.deck.pop()
                print(
                    '------------------------------------------------------------------------------------------------------------------')
                print("p1 player, money, hand : {} {} {}{}".format(p1.name, p1.bal, p1.hand1, p1.hand2))
                print("p2 player, money hand: {} {} {}{}".format(p1.name, p2.bal, p2.hand1, p2.hand2))
                # print('------------------------------------------------------------------------------------------------------------------')
                # env.print = True

                for i in range(10000):
                    # p1, p2 번갈아가면서 게임을 진행
                    # p1(1) -> p2(-1)
                    reward, done = env.move(p1, p2, (-1) ** i)
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
                print("table= {} p1({}) = {} p2({}) = {} draw = {}".format(env.table, p1.name, p1_score, p2.name, p2_score,
                                                                           draw_score))
                if answer == 'y':
                    pass
                else:
                    print("Good Game!")
                    print("\n현재 라운드: {}\n{} 승리 횟수: {} {} 승리 횟수: {} 비긴 횟수: {}".format(j, p1.name, p1_score, p2.name, p2_score,
                                                                                     draw_score))
                    print("{} 잔고: {}, {} 잔고: {} 잔고합계 {}".format(p1.name, p1.bal, p2.name, p2.bal, p1.bal + p2.bal))
                    print("수행 시간: {}".format(time.time() - start))

