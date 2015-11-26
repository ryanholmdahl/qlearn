import play_game,qlearn,policy,util

#Does some q learning on the hdmdp.
def qlsimulate(hdmdp, rl, numTrials=10, maxIterations=1000, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        hdmdp.restart()
        state = hdmdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state)
            newState, reward = hdmdp.succAndReward(state, action)
            if newState == None:
                rl.incorporateFeedback(state, action, 0, None)
                break

            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= hdmdp.discount()
            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        totalRewards.append(totalReward)
    return totalRewards

#Uncomment to test qlearning
# game = play_game.BSGame(3,[2,2],0,verbose=False)
# apolicy1 = policy.SketchyPolicy(game,0.5)
# apolicy2 = policy.SketchyPolicy(game,0.25)
# game.setPolicies([None,apolicy1.decision,apolicy2.decision])
# qlearning = qlearn.QLearningAlgorithm(game.actions,game.discount(),qlearn.snazzyFeatureExtractor)
# qlsimulate(game,qlearning,numTrials=10000,verbose=True)
# qlearning.explorationProb = 0
# game.resetWins()
# qlsimulate(game,qlearning,numTrials=1000,verbose=True)
# print game.wins

#Tests an hdmdp with the agent following the agent_decision policy.
def allsetsimulate(hdmdp, agent_decision, numTrials=10, maxIterations=1000, verbose=False):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        hdmdp.restart()
        state = hdmdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            if state[0] == "someone_wins":
                action = "end_game"
            else:
                action = agent_decision(state)
            newState, reward = hdmdp.succAndReward(state, action)
            if newState == None:
                break

            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            totalReward += totalDiscount * reward
            totalDiscount *= hdmdp.discount()
            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        totalRewards.append(totalReward)
    return totalRewards

# Uncomment to test strict policy following for the agent
# game = play_game.BSGame(3,[4,4],2,verbose=False)
# ppolicy = policy.SketchyPolicy(game,0.5)
# apolicy1 = policy.SketchyPolicy(game,0.5)
# apolicy2 = policy.SketchyPolicy(game,0.5)
# apolicy3 = policy.SketchyPolicy(game,0.5)
# game.setPolicies([apolicy1.decision,apolicy2.decision,apolicy3.decision])
# totalRewards = allsetsimulate(game,ppolicy.decision,numTrials=1000,verbose=False)
# print game.wins