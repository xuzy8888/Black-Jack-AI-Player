import copy
import random

from game import Game, states

HIT = 0
STAND = 1
DISCOUNT = 0.95 #This is the gamma value for all value calculations

class Agent:
    def __init__(self):

        # For MC values
        self.MC_values = {} # Dictionary: Store the MC value of each state
        self.S_MC = {}      # Dictionary: Store the sum of returns in each state
        self.N_MC = {}      # Dictionary: Store the number of samples of each state
        # MC_values should be equal to S_MC divided by N_MC on each state (important for passing tests)

        # For TD values
        self.TD_values = {}  # Dictionary storing the TD value of each state
        self.N_TD = {}       # Dictionary: Store the number of samples of each state

        # For Q-learning values
        self.Q_values = {}   # Dictionary storing the Q-Learning value of each state and action
        self.N_Q = {}        # Dictionary: Store the number of samples of each state

        # Initialization of the values
        for s in states:
            self.MC_values[s] = 0
            self.S_MC[s] = 0
            self.N_MC[s] = 0
            self.TD_values[s] = 0
            self.N_TD[s] = 0
            self.Q_values[s] = [0,0] # First element is the Q value of "Hit", second element is the Q value of "Stand"
            self.N_Q[s] = 0
        # NOTE: see the comment of `init_cards()` method in `game.py` for description of game state       
        self.simulator = Game()

    # NOTE: do not modify
    # This is the policy for MC and TD learning. 
    @staticmethod
    def default_policy(state):
        user_sum = state[0]
        user_A_active = state[1]
        actual_user_sum = user_sum + user_A_active * 10
        if actual_user_sum < 14:
            return 0
        else:
            return 1

    # NOTE: do not modify
    # This is the fixed learning rate for TD and Q learning. 
    @staticmethod
    def alpha(n):
        return 10.0/(9 + n)
    
    def MC_run(self, num_simulation, tester=False):
        # Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            # Do not modify the following three lines
            if tester:
                self.tester_print(simulation, num_simulation, "MC")
            self.simulator.reset()  # Restart the simulator

            episode = self.simulator.simulate_sequence(self.default_policy)
            for i in range(len(episode)):
                self.N_MC[episode[i][0]] += 1
                self.S_MC[episode[i][0]] += (episode[len(episode)-1][1] * (DISCOUNT**(len(episode)-i-1)))
                self.MC_values[episode[i][0]] = self.S_MC[episode[i][0]] / self.N_MC[episode[i][0]]

            # TODO
            # Note: Do not reset the simulator again in the rest of this simulation
            # Hint: Go through game.py file and figure out which functions will be useful
            # Useful variables:
            #     - DISCOUNT
            #     - self.MC_values     (read comments in self.__init__)
            # remember to update self.MC_values, self.S_MC, self.N_MC for the autograder!
    
    def TD_run(self, num_simulation, tester=False):
        # Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            # Do not modify the following three lines
            if tester:
                self.tester_print(simulation, num_simulation, "TD")
            self.simulator.reset()

            state = self.simulator.state
            pre_rwd = 0
            while state is not None:
                nxt_tuple = self.simulator.simulate_one_step(self.default_policy(state))
                nxt_state = nxt_tuple[0]
                nxt_reward = nxt_tuple[1]
                self.N_TD[state] += 1
                
                curr_value = self.TD_values[state]
                alpha = self.alpha(self.N_TD[state])

                if nxt_state is None:
                    discount_part = 0
                else:
                    discount_part = DISCOUNT * self.TD_values[nxt_state]

                self.TD_values[state] = curr_value + alpha * (pre_rwd + discount_part - curr_value)

                pre_rwd = nxt_reward
                state = nxt_state

            # TODO
            # Note: Do not reset the simulator again in the rest of this simulation
            # Hint: Go through game.py file and figure out which functions will be useful
            # Hint: The learning rate alpha is given by "self.alpha(...)"
            # Useful variables/funcs:
            #     - DISCOUNT
            #     - self.TD_values  (read comments in self.__init__)
            # remember to update self.TD_values and self.N_TD for the autograder!
                
    def Q_run(self, num_simulation, tester=False):
        # Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):
            # Do not modify the following three lines
            if tester:
                self.tester_print(simulation, num_simulation, "Q")
            self.simulator.reset()

            state = self.simulator.state
            cur_rwd = 0
            eps = 0.4
            
            while state is not None:
                action = self.pick_action(state,eps)
                self.N_Q[state] += 1
                nxt_tuple = self.simulator.simulate_one_step(action)
                nxt_state = nxt_tuple[0]
                nxt_reward = nxt_tuple[1]

                cur_value = self.Q_values[state][action]

                if nxt_state is None:
                    nxt_max = 0
                else:
                    nxt_max = max(self.Q_values[nxt_state][0],self.Q_values[nxt_state][1])

                discount = DISCOUNT*nxt_max
                aplha = self.alpha(self.N_Q[state])

                self.Q_values[state][action] = cur_value + aplha * (cur_rwd + discount - cur_value)

                cur_rwd = nxt_reward
                state = nxt_state



            # TODO
            # Note: Do not reset the simulator again in the rest of this simulation
            # Hint: Go through game.py file and figure out which functions will be useful
            # Hint: The learning rate alpha is given by "self.alpha(...)"
            # Hint: Implement epsilon-greedy method in "self.pick_action(...)"
            # Useful variables:
            #     - DISCOUNT
            #     - self.Q_values  (read comments in self.__init__)
            # remember to update self.Q_values, self.N_Q for the autograder!

    def pick_action(self, s, epsilon):
        # TODO: Replace the following random return value with the epsilon-greedy strategy
        if random.random()<epsilon:
            return random.randint(0,1)
        else:
            if self.Q_values[s][0]>=self.Q_values[s][1]:
                return 0
            else:
                return 1

    #Note: do not modify
    def autoplay_decision(self, state):
        hitQ, standQ = self.Q_values[state][HIT], self.Q_values[state][STAND]
        if hitQ > standQ:
            return HIT
        if standQ > hitQ:
            return STAND
        return HIT #Before Q-learning takes effect, just always HIT

    # NOTE: do not modify
    def save(self, filename):
        with open(filename, "w") as file:
            for table in [self.MC_values, self.TD_values, self.Q_values, self.S_MC, self.N_MC, self.N_TD, self.N_Q]:
                for key in table:
                    key_str = str(key).replace(" ", "")
                    entry_str = str(table[key]).replace(" ", "")
                    file.write(f"{key_str} {entry_str}\n")
                file.write("\n")

    # NOTE: do not modify
    def load(self, filename):
        with open(filename) as file:
            text = file.read()
            MC_values_text, TD_values_text, Q_values_text, S_MC_text, N_MC_text, NTD_text, NQ_text, _  = text.split("\n\n")
            
            def extract_key(key_str):
                return tuple([int(x) for x in key_str[1:-1].split(",")])
            
            for table, text in zip(
                [self.MC_values, self.TD_values, self.Q_values, self.S_MC, self.N_MC, self.N_TD, self.N_Q], 
                [MC_values_text, TD_values_text, Q_values_text, S_MC_text, N_MC_text, NTD_text, NQ_text]
            ):
                for line in text.split("\n"):
                    key_str, entry_str = line.split(" ")
                    key = extract_key(key_str)
                    table[key] = eval(entry_str)

    # NOTE: do not modify
    @staticmethod
    def tester_print(i, n, name):
        print(f"\r  {name} {i + 1}/{n}", end="")
        if i == n - 1:
            print()
