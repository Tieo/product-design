
import random
import csv
import pandas as pd
from itertools import combinations
''' for test
Q1 = (('s', 7), 1546)
Q11 = (('s', 7), 1546)
Q2 = (1546 / 1, 1)

Q = {Q1: Q2}
print(Q)
if Q11 in Q:
    print(Q)

if Q1 == Q11:
    print(1)'''

#Dealer
class Dealer:
    def __init__(self):
        self.fold = 0  # 포기한 사람의 수
        self.turn = 0 # 턴 카운터
        #comcard = []  # 공용패
        self.pot = 0  ##확정 판돈
        self.table = []  # 베팅금 임시보관
        self.count = 0
        #self.cnt = 0
        self.comdeck = None

    def make_comcard(self, turn):
        '''하나의 리스트에서 n개씩 뽑는 모든 조합 구하기: 순서 상관 없으므로 combination 상관 있으면 permutation
            item = []
            from itertools import combinations
            list(combinations(item, n) <- s2, s5, s6, s7 list '''
        deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
        random.shuffle(deck)
        if self.turn == 0:
            n = 2
        elif self.turn == 1:
            n = 5
        elif self.turn == 2:
            n = 6
        else:
            n = 7

        self.comdeck = list(combinations(deck, n))
        #print('comdeck', self.comdeck)
        self.count = len(self.comdeck)
        #return comdeck

    def state(self, turn):
        if self.comdeck:
            pass
            '''
        if turn == 0:
            for i in range(3):
                comcard.append(self.comdeck.pop())
        elif turn == 1:
            for i in range(6):
                comcard.append(self.comdeck.pop())
        elif turn == 2:
            for i in range(7):
                comcard.append(self.comdeck.pop())
        else:
            for i in range(8):
                comcard.append(self.comdeck.pop())'''
        else:
            self.make_comcard(turn)
        comcard = []
        comcard.append(self.comdeck.pop())

        s = (turn, comcard)
        return s

    def pf_reward(self, handcheck, ai_action):
        print('hc, a', handcheck, ai_action)
        '''if handcheck == 'fold' and ai_action >0:
            print('ai folded')
            if ai_action >= 0:  # 콜, 레이즈, 체크
                rwd = -1
            else:  # 폴드한 경우
                rwd = +1
        else:
            if ai_action >= 0:  # 콜, 레이즈, 체크
                rwd = +1
            else:  # 폴드한 경우
                rwd = -1'''
        if (handcheck == 'fold') and (ai_action > 0):
            print('ai folded')
            #if ai_action >= 0:  # 콜, 레이즈, 체크
            rwd = -1
        elif (handcheck == 'fold') and (ai_action < 0):   # 폴드한 경우
            rwd = +1

        elif (handcheck != 'fold') and (ai_action > 0):
            #if ai_action >= 0:  # 콜, 레이즈, 체크
            rwd = +1
        else:  # 폴드한 경우
            rwd = -1

        return rwd

    def reward(self, ai_action, aipt, table, someonebet):
        tbratio = (someonebet[-1] / table + someonebet[-1]) * 100 #판돈 증가 비율

        #   < 카드 족보가 좋은 경우 >
        if aipt == 2:  # 원페어
            if (ai_action == 0) or (ai_action >= 0):  # 콜, 레이즈, 체크
                r = +1 * tbratio
            else:  # 폴드한 경우
                r = - 1
        if aipt >= 3:  # 투페어 이상
            if (ai_action == 0) or (ai_action >= 0):  # 콜, 레이즈, 체크
                r = +3 * tbratio
            else:  # 폴드한 경우
                r = - 3

         #   < 카드 족보가나쁜 경우, 하이카드 >

        if ((aipt >= 1) and (aipt < 2)) and someonebet[-1] == 0:

            if (ai_action == 0) or (ai_action >= 0):  # 콜, 레이즈, 체크
                r = -0 * tbratio
            else:  # 폴드한 경우
                r = +0

        elif ((aipt >= 1) and (aipt < 2)) and (someonebet[-1] >= 500) and (someonebet[-1] < 1000):
            if (ai_action == 0) or (ai_action >= 0):  # 콜, 레이즈, 체크
                r = -1 * tbratio
            else:  # 폴드한 경우
                r = +1

        elif ((aipt >= 1) and (aipt < 2)) and (someonebet[-1] > 1000):
            if (ai_action == 0) or (ai_action >= 0):  # 콜, 레이즈, 체크
                r = -3 * tbratio
            else:  # 폴드한 경우
                r = +3
        else:
            pass

        return r

    def episode_end(self): # 턴 별로 마무리를 지어줘야 함. turn 0 에서 52 중 2개 뽑는 경우의 수가 끝났는지
        #self.cnt += 1
        #print(self.cnt)
        print(self.count)
        self.count -=1
        if self.count > 0:
            return 0
        else:
            return 1

    def someone_bet(self, turn):
        if turn == 0:
            lowlimit = 400
        else:
            lowlimit = 200
        someonebet = []
        someonebet.append(random.randint(lowlimit, 2000))
        return someonebet


# AI 플레이어
class Agent:
    def __init__(self):
        self.Qt = {}

    def action(self, s, episode): # 몬테카를로 컨트롤에서 행동

        if s not in episode: #explore
            if s[0] == 0:
                lowlimit = 400
            else:
                lowlimit = 200
            low_rand = random.randint(lowlimit, 2000)
            rand_list = [-1, 0, low_rand]  # fold, call/check, raise
            a = random.choice(rand_list)  # 랜덤한 A[t] 선택 -> Explore Start #처음 맞이하는 상태이면 랜덤 숫자
            return a

        else: #exploit        '''Q(S[t], A[t])가 최대인 A[t]를 Episode에서 선택
            '''s가 같은 경우에 same_s_list 에 삽입.
                           rwd_list로 각 원소의 3번째 값만 따로 리스트로 뽑고,
                           rwd_list 리스트에서 Max 값의 인덱스 찾기
                           행동 a는 same_s_list[Maxind][1]'''

            same_s_list = []
            for i in range(len(episode)):
                if s == episode[i][0]:
                    same_s_list.append(episode[i])

            rwd_list = []
            for i in range(len(same_s_list)):
                rwd_list.append(same_s_list[i][2])

            max_rwd_ind = rwd_list.index(max(rwd_list))

            a = same_s_list[max_rwd_ind][1]

            return a

    def hand_check(self, hand1, hand2): #핸드체크, 프레플랍 단계 먼저 자신에게 주어진 카드 정보를 분석한다.
        premium = [('p', 14,14),('p',13,13),('p',12,12),('s',14,13),('p',11,11),('s',14,12),('s',13,12),('s',14,11),('s',13,11),('p',10,10),('o',14,13),('s',14,10),('s',12,11),('s',13,10),('s',12,10),('s',11,10),('p',9,9)]
        special = [('o',14,12),('s',14,9),('o',13,12),('p',8,8),('s',13,9),('s',10,9),('s',14,8),('s',12,9),('s',11,9),('o',14,11),('s',14,5),('p',7,7),('s',14,7),('o',13,11),('s',14,4),('s',14,3),('s',14,6)]
        good = [('o',12,11),('p',6,6),('s',13,8),('s',10,8),('s',14,2),('s',9,8),('s',11,8),('o',14,10),('s',12,8),('s',13,7),('o',13,10),('p',5,5),('o',11,10),('s',8,7),('o',12,10),('p',4,4),('p',3,3),('p',2,2)]
        # 숫자 비교 후 pair인지 확인(pair이면 p, 아니면 문자 확인으로 넘어감), 문자 확인해서 일치하는지 확인(불일치 하면 o, 일치하면 s ),  숫자 조합해서 하나의 튜플로 제작
        if hand1[1] == hand2[1]:
            tup1 = 'p'
        else:
            if hand1[0] == hand2[0]:
                tup1 = 's'
            else:
                tup1 = 'o'

        if hand1[1] > hand2[1]: # 숫자 큰 게 앞으로 오게 함
            tup2, tup3 = hand1[1], hand2[1]
        else:
            tup2, tup3 = hand2[1], hand1[1]

        tup = (tup1,tup2,tup3) #튜플 생성

        if premium.count(tup) == 1:
            return ('premium')
        elif special.count(tup) == 1:
            return ('special')
        elif good.count(tup) == 1: #판단
            return ('good')
        else:
            return ('fold')


    def policy(self, s, hand1, hand2): # Q table에서 고르는 것, 실제 게임에서 행동
        s = self.hand_check(hand1, hand2)
        if s == 'fold':
            return -1
        else:
            find_maxr_list , a_list= [], []
            for stp, atp in self.Qt.items(): #Qt 키는 stp에, 값은 atp에 저장
                if s == stp[0]: # 키의 1번째 원소와 s 가 같으면
                    find_maxr_list.append(atp[0]) # 값의 첫번째 원소를 리스트에 저장 - 보상
                    a_list.append(stp[1]) # 행동도 저장, 위 리스트와 같은 순서로 저장됨.
            max_ind = find_maxr_list.index(max(find_maxr_list)) #보상이 최대인 인덱스 찾기
            a = a_list[max_ind]

        return a


    def make_qtable(self, st, at, episode):  # return도 입력으로 받아야 함. a 선택 횟수랑, 이건 Qt를 만들자 @@@@@@@@@@@@@@@@

        key = (st, at) #(ai의 상태, ai의 행동)

        a_cnt = 0
        find_maxr_list = []
        find_maxr_alist = []
        #print(episode)
        #print(st, at, st[0])
        #print(episode[0], episode[0][0], episode[0][0][0], episode[0][0][1][0], episode[0][1], episode[0][2])
        for i in episode:  # episode는 리스트!
            #print(i)
            stmp = (i[0][0], i[0][1][0])
            #print(st, stmp)
            if (st == stmp): # and (at == i[1]):  # 에피소드에서 s,a가 같은 모든 경우에 대해
                find_maxr_list.append(i[2])  # 보상을 저장한다.
                find_maxr_alist.append(i[1]) #행동을 저장
                a_cnt += 1  # a가 선택된 횟수
                print('@@@@@@@@@@@@@@@@@@@@@@@@')
                print(find_maxr_alist, find_maxr_list)
        g = sum(find_maxr_list) # 보상의 합은 수익 G
        arg_return = g/a_cnt # 보상의 평균
        value = (arg_return, a_cnt) # 값은 (보상, a 선택횟수)

        self.Qt[key] = value
        f = open('Qt.csv', 'a', encoding='utf-8', newline='')
        wr = csv.writer(f)
        wr.writerow(self.Qt)
        f.close()

        return self.Qt

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
                if numcards[i] - 1 == numcards[i + 1] and numcards[i + 1] - 1 == numcards[i + 2] and numcards[i + 2] - 1 == \
                        numcards[i + 3] and numcards[i + 3] - 1 == numcards[i + 4]:
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


# MonteCarlo Control
class MonteCarlo:
    #딜러 초기화 #ai 초기화
    mc_dlr = Dealer()
    mc_ai = Agent()

    episode = []

    def make_episode(self, turn):
        while True:
            #low_rand = random.randint(lowlimit, 2000)
            #rand_list = [-1, 0, low_rand] #fold, call/check, raise

            s = self.mc_dlr.state(turn)
            if s not in self.episode:  # 이라면 #플레이어가 A[t] 선택
                #a = random.choice(rand_list)  # 랜덤한 A[t] 선택 -> Explore Start #처음 맞이하는 상태이면 랜덤 숫자
                a = self.mc_ai.action(s, self.episode)

            else:  # if S[t] in S 인 경우 에피소드에서 고르는 것
                a = self.mc_ai.action(s, self.episode)
                '''Q(S[t], A[t])가최대인A[t]를Episode에서 선택
                s가 같은 경우에 same_s_list 에 삽입.
                rwd_list로 각 원소의 3번째 값만 따로 리스트로 뽑고,
                rwd_list 리스트에서 Max 값의 인덱스 찾기
                행동 a는 same_s_list[Maxind][1]

                same_s_list = []
                for i in range(len(episode)):
                    if s == self.episode[i][0]
                        same_s_list.append(self.episode[i])

                rwd_list = []
                for i in range(len(same_s_list)):
                    rwd_list.append(same_s_list[i][2])

                max_rwd_ind = rwd_list.index(max(rwd_list))

                a = same_s_list[max_rwd_ind][1]'''

            if self.mc_dlr.turn == 0: #프리플롭인 경우
                cards = s[1]
                print(cards[0][0])
                hc = self.mc_ai.hand_check(cards[0][0],cards[0][1]) # 핸드 평가
                print(hc)
                r = self.mc_dlr.pf_reward(hc, a) # 보상
                print('s,a,r', s, a, r)
                self.episode.append((s, a, r))
                #print(self.episode)
                if self.mc_dlr.episode_end() == 1:
                    self.mc_dlr.turn += 1
                    break

            else:
                cards = s[1]
                aipt = self.mc_ai.aipoint(cards[2:], cards[0], cards[1])
                sb = self.mc_dlr.someone_bet(self.mc_dlr.turn)
                r = self.mc_dlr.reward(a, aipt, table, someonebet=sb)
                self.episode.append((s, a, r))
                if self.mc_dlr.episode_end():
                    self.mc_dlr.turn += 1
                    break

            #self.episode.append((s, a, r))
            #딜러가    A[t] 받아서 S[t + 1], Episode 종료여부, Reward R[t + 1] 반환
            #self.episode.append((S[t], A[t], R[t + 1]))

        '''생성된 Episode = {(S[0], A[0], R[0 + 1]), (S[1], A[1], R[1 + 1]), ..., (S[t - 1], A[t - 1], R[t])}
        를  반환'''
        return self.episode

    def val_func_updt(self): #이게 Qt에서 값을 업데이트 @@@@@@@@@@@@@@@@
        epic = self.episode
        g = 0
        for i in epic:
            g = g + i[2]
            self.mc_ai.Qt[i[0],i[2]][0] = self.mc_ai.Qt[i[0],i[2]][0] + (self.mc_ai.Qt[i[0],i[2]][0]+g)/self.mc_ai.Qt[i[0],i[2]][1]


count = 0  ##게임 횟수

while 1:
    fold = 0  # 포기한 사람의 수
    global turn  # 턴 카운터
    turn = 0
    comcard = []  # 공용패
    pot = 0  ##확정 판돈
    table = []  # 베팅금 임시보관

    count += 1
    deck = [(suit, i) for suit in ["s", "h", "d", "c"] for i in range(2, 15)]  ##카드 덱 만들기, 튜플로 구성된 리스트
    random.shuffle(deck)

    mc = MonteCarlo()

    ai = Agent()
    dlr = Dealer()

    while 1:
        # print(players)
        turns = ['Pre-flop', 'Flop', 'Turn', 'River(Last turn)']

        print('---------------------- %s ----------------------\n' % turns[turn])
        epics = mc.make_episode(turn)

        if turn == 0:
            lowlimit = 400
        else:
            lowlimit = 200
        # st = State(turn, tuple(comcard), pot, tuple(table), fold)
        if turn == 0:
            for i in range(2):  ##카드 3장 깔기
                comcard.append(deck.pop())
        elif turn == 1:
            for i in range(3):  ##카드 3장 깔기
                comcard.append(deck.pop())
            print(comcard)

        elif turn < 4:  ##턴이 2, 3 일때 카드 1장씩 깔기
            comcard.append(deck.pop())
            print(comcard)
        elif turn == 4:  # 쇼다운으로 넘어감
            print(comcard)

        if turn == 4:
            break

        st = turn, tuple(comcard)
        at = ai.action(st, epics)
        qt = ai.make_qtable(st, at, epics)
        turn += 1

    print(st, at, qt, 'State Action Agent')
    f = open('data.csv', 'a', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(qt)
    f.close()

    #df = pd.DataFrame(qt)
    #df.to_csv("E:\2020\종합설계\holdem\data.csv", header=False, index=False)

    break

csv_data = pd.read_csv('data.csv', header = None)
print('\nread_csv', csv_data)
