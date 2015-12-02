import play_game,policy,simulators,qlearn,random

# Acquires the win rate of a learning SketchyPolicy agent with sketchiness 0.5 and confidence 1
# in each of the nplayers positions. A properly formatted call might look like:
#   baseline(3,5,4,5000),
# in which case the deck would be [4,4,4,4,4]. Generally, the wins should be fairly evenly distributed,
# favoring earlier players.
def baseline(nplayers,num_card_values,num_cards,trials,verbose=False):
    print "Determining baseline using learning SketchyPolicy agents."
    for i in range(nplayers):
        print "Simulating agent",i,"..."
        game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],i,verbose=False)
        ppolicy = policy.SketchyPolicy(game,0.5,learn=True)
        apolicies = []
        for t in range(nplayers):
            apolicies.append(policy.SketchyPolicy(game,0.5,learn=True).decision)
        game.setPolicies(apolicies)
        simulators.allsetsimulate(game,ppolicy.decision,numTrials=trials,verbose=verbose)
        print "Wins observed:",game.wins
        print "Agent in position",i,"has a win rate of ",str(float(game.wins[i])/sum(game.wins))
        game.resetWins()

# Acquires the win rate of a learning SketchyPolicy agent with sketchiness 0.5 and confidence 1
# in each of the nplayers positions. This agent can see the last play and will perfectly call BS
# on it. Formatting is the same as a call to baseline. Generally, the win rate for the oracle is above
# 90%.
def oracle(nplayers,num_card_values,num_cards,trials,verbose=False):
    print "Determining oracle using learning SketchyPolicy agents."
    for i in range(nplayers):
        print "Simulating agent",i,"..."
        game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],i,verbose=False)
        ppolicy = policy.SketchyPolicy(game,0.5,learn=True)
        apolicies = []
        for t in range(nplayers):
            apolicies.append(policy.SketchyPolicy(game,0.5,learn=True).decision)
        game.setPolicies(apolicies)
        simulators.allsetsimulate(game,ppolicy.decision,numTrials=trials,oracle=True,verbose=False)
        print "Wins observed:",game.wins
        print "Agent in position",i,"has a win rate of ",str(float(game.wins[i])/sum(game.wins))
        game.resetWins()

# Uses qlearning to create an agent against some adversaries. The adversaries will have random sketchiness and confidence
# unless lists are passed to the respective parameters. The algorithm learns for |learn_trials| iterations before being
# evaluated for |test_trials| iterations.
def qlearn_test(nplayers,num_card_values,num_cards,agent,learn_trials,test_trials, featureExtractor = qlearn.snazzyFeatureExtractor, explorationProb = 0.2, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Running qlearning as agent",agent,"."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=False)
    if sketch_list is None:
        sketch_list = [random.random() if _ is not agent else 0 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [random.random() if _ is not agent else 0 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [True for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=True).decision)
    game.setPolicies(apolicies)
    qlearning = qlearn.QLearningAlgorithm(game.actions,game.discount(),featureExtractor,explorationProb=explorationProb)
    print "Learning..."
    simulators.qlsimulate(game,qlearning,numTrials=learn_trials,verbose=verbose)
    print "Learning complete. Now simulating tests..."
    qlearning.explorationProb = 0
    game.resetWins()
    simulators.qlsimulate(game,qlearning,numTrials=test_trials,verbose=verbose)
    print "Wins observed:",game.wins
    print "Agent in position",agent,"has a win rate of",str(float(game.wins[agent])/sum(game.wins))

# Runs |trials| games of sketchy policies playing against one another. Ideally, the agent parameter should make no difference,
# but it is available for testing purposes (to ensure that it has no effect).
def allsketchy_test(nplayers, num_card_values, num_cards, trials, agent = 0, sketch_list = None, confidence_list = None, learn_list = None, verbose = False):
    print "Running an all-sketchy simulation."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=False)
    if sketch_list is None:
        sketch_list = [random.random()  for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [random.random() for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [True for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
    game.setPolicies(apolicies)
    print "Simulating..."
    simulators.allsetsimulate(game,apolicies[agent],numTrials=trials,verbose=verbose)
    print "Wins observed:",game.wins
    print "Agents have winrates of",[float(game.wins[i])/sum(game.wins) for i in range(nplayers)]