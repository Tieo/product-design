import pandas as pd
import random

class agent:
    fold = 0

    def __init__(self):
        self.count_list = []
        self.count_list2 =[]
        self.turn_list = []
        self.turn_list2 = []
        self.point_list = []
        self.Sbet_list = [] #someone bet list
        self.Abet_list = [] #agent bet list 
        self.comcard1_list = []
        self.comcard2_list = []
        self.comcard3_list = []
        self.comcard4_list = []
        self.comcard5_list = []
        self.hand1_list = []
        self.hand2_list = []
        self.action_list =[]
        self.money_list = [] #잔고
        self.pot_list = []

    def name(self, name):
        self.name = name
        return self.name

    def environment(self, count, turn, aipt, someonebet, comcard, hand1, hand2, agent_action): #게임 데이터
        self.count_list.append(count)
        self.turn_list.append(turn)
        self.point_list.append(aipt)
        self.Sbet_list.append(someonebet[-1])
        if len(comcard) == 3:
            self.comcard1_list.append(comcard[0])
            self.comcard2_list.append(comcard[1])
            self.comcard3_list.append(comcard[2])
            self.comcard4_list.append(None)
            self.comcard5_list.append(None)

        elif len(comcard) == 4:
            self.comcard1_list.append(comcard[0])
            self.comcard2_list.append(comcard[1])
            self.comcard3_list.append(comcard[2])
            self.comcard4_list.append(comcard[3])
            self.comcard5_list.append(None)
        elif len(comcard) == 5:
            self.comcard1_list.append(comcard[0])
            self.comcard2_list.append(comcard[1])
            self.comcard3_list.append(comcard[2])
            self.comcard4_list.append(comcard[3])
            self.comcard5_list.append(comcard[4])
        self.hand1_list.append(hand1)
        self.hand2_list.append(hand2)
        self.action_list.append(agent_action)
        print(self.hand1_list)

    def bet_update(self, count, turn, bet, money, pot):
        self.count_list2.append(count)
        self.turn_list2.append(turn)
        self.Abet_list.append(bet)
        self.money_list.append(money)
        self.pot_list.append(pot)

    def show_env(self):
        ENVdata = {'count':self.count_list, 'turn':self.turn_list, 'point': self.point_list, 'someonebet':self.Sbet_list, 'comcard1':self.comcard1_list, 'comcard2':self.comcard2_list, 'comcard3':self.comcard3_list, 'comcard4':self.comcard4_list, 'comcard5':self.comcard5_list, 'hand1':self.hand1_list, 'hand2':self.hand2_list} 
        ENVdf = pd.DataFrame(ENVdata)
        return ENVdf

    def show_bet(self):
        BETdata = {'count':self.count_list2, 'turn':self.turn_list2, 'bet':self.Abet_list, 'money':self.money_list, 'pot':self.pot_list}

        BETdf = pd.DataFrame(BETdata)
        return BETdf


		

    def aipoint(self, comcard, hand1, hand2): #컴퓨터가 자신의 핸드 + 커뮤니티 족보를 판단 
        flush = 0
        threeKind = 0
        fourKind =0
        pairCount = 0
        full = 0

        handset = [hand1, hand2] 
        cardset = comcard[:] + handset[:]
        cards = cardset
        cards.sort(key = lambda x:-x[1]) #두번째 튜플로 내림차순 정렬
        alphacards = [x[0] for x in cards] #알파벳 모음
        numcards = []
        for i in cards:
            numcards.append(i[1])

        if alphacards.count('s') == 5 or alphacards.count('d') == 5 or alphacards.count('h') == 5 or alphacards.count('c') == 5:   # 무늬가 5장 같을 경우 ( 플러쉬)
            flush = 1

        for i in range(2,15):
            if numcards.count(i) == 4: #포카드 
                fourKind = 1
            elif numcards.count(i) == 3: #쓰리카드
                threeKind = 1
            elif numcards.count(i) == 2: # 페어
                pairCount += 1
        
        if threeKind and pairCount:
            full = 1 #풀하우스 

        if len(cards) >=5 :
            for i in range (0, len(cards)-4): #스트레이트 (5장의 카드가 연속)
                if numcards[i]-1 == numcards[i+1] and numcards[i+1]-1 == numcards[i+2] and numcards[i+2]-1 == numcards[i+3] and numcards[i+3]-1 == numcards[i+4]:
                    if alphacards[i] == alphacards[i+1] == alphacards[i+2] == alphacards[i+3] == alphacards[i+4]:#스트레이트인 카드들의 무늬가 같음
                        if numcards[0] == 14: #무늬가 같은데 가장 큰 숫자가 14
                            #print('로열플러쉬!') 
                            return 10
                        #print('스트레이트 플러쉬!') 
                        return 9
                    #print('스트레이트!')
                    return 5

        if fourKind == 1:
            return 8       #포카드

        elif full == 1:
            return 7        #풀하우스

        elif flush == 1:
            return 6        # 플러쉬

        elif threeKind == 1:
            return 4        #트리플

        elif pairCount >= 2:
            return 3        #투페어

        elif pairCount == 1:
            return 2        #원페어

        else:
            return 0.1*numcards[0]         #하이카드

    def turnaction(self, count, turn, aipt, someonebet, comcard, hand1, hand2): #턴 별 액션 
        print(self.name+":")
        #행동을 취할때마다 환경 데이터 업데이트        
        if 2000 in someonebet:
        	agent_action = random.choices(range(1,3,1), weights=[0.5,0.5])
        	self.environment(count, turn,aipt, someonebet, comcard, hand1, hand2, agent_action)
        	return agent_action
        else:
        	agent_action = random.choices(range(1,4,1))
        	self.environment(count, turn,aipt, someonebet, comcard, hand1, hand2, agent_action)
        	return agent_action



    def bet(self, count, turn, money,pot ): #베팅함수
        agentbet = random.randint(0,2001)
        self.bet_update(count, turn, agentbet, money, pot)
        return agentbet


    def showhand(self): #패공개
        return 1

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




#@@@@@@@@@@@@@@@@@TEST



#agent = agent()
#count = 0
#turn = 0
#money = 5000
#pot = 300
#someonebet = []
#someonebet.append(0)
#comcard = [('s',3),('c',14),('s',6)]
#hand1 = ('s',5)
#hand2 = ('d',11)

#print('aipt------')
#agent.name('agent')
#aipt = agent.aipoint(comcard, hand1, hand2)
#print(aipt)
#print('turnaction---')
#print(agent.turnaction(count, turn, aipt, someonebet, comcard, hand1, hand2))
#print('bet----')
#print(agent.bet(count, turn, money, pot))


#print('----ENV data====')
#env_data = agent.show_env()
#print(env_data.head())
#print('---BET data----')
#bet_data = agent.show_bet()
#print(bet_data.head())
