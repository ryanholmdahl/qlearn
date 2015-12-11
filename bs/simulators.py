#Does some q learning on the hdmdp.
def rlsimulate(hsmdp, rl, numTrials=10, maxIterations=1000, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        hsmdp.restart()
        state = hsmdp.startState()
        if not state: continue
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state)
            newState, reward = hsmdp.succAndReward(state, action)
            if not newState:
                rl.incorporateFeedback(state, action, 0, None)
                break

            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= hsmdp.discount()
            state = newState
        if verbose:
            print "\ntrial", trial, "reward", totalReward
        totalRewards.append(totalReward)
    return totalRewards

#Tests an hdmdp with the agent following the agent_decision policy.
def allsetsimulate(hsmdp, agent_decision, numTrials=10, maxIterations=1000, oracle=False, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        hsmdp.restart()
        state = hsmdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            if not state: break
            if state[0] == "someone_wins":
                action = "end_game"
            else:
                if not oracle or len(state) == 6:
                    action = agent_decision(state, hsmdp.agent_index)
                else:
                    action = "pass" if hsmdp.lastPlayIsHonest() else "bs"

            newState, reward = hsmdp.succAndReward(state, action)

            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            totalReward += totalDiscount * reward
            totalDiscount *= hsmdp.discount()
            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        totalRewards.append(totalReward)
    return totalRewards

# Runs a simulation with a user-input human player.
def humansimulate(hsmdp, maxIterations=1000):
    hsmdp.verbose = True
    hsmdp.restart()
    state = hsmdp.startState()
    sequence = [state]
    totalDiscount = 1
    totalReward = 0
    for _ in range(maxIterations):
        if not state: break
        if state[0] == "someone_wins":
            action = "end_game"
        else:
            print "Current state:", state
            action = None
            while action not in hsmdp.actions(state):
                action = input("Enter an action: ")
            print "Action interpreted as", action

        newState, reward = hsmdp.succAndReward(state, action)

        sequence.append(action)
        sequence.append(reward)
        sequence.append(newState)

        totalReward += totalDiscount * reward
        totalDiscount *= hsmdp.discount()
        state = newState
    print "Game complete (totalReward = %s): %s" % (totalReward, sequence)
