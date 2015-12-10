import play_game,policy,simulators,qlearn,random,model_based

# Acquires the win rate of a learning SketchyPolicy agent with sketchiness 0.5 and confidence 1
# in each of the nplayers positions. A properly formatted call might look like:
#   baseline(3,5,4,5000),
# in which case the deck would be [4,4,4,4,4]. Generally, the wins should be fairly evenly distributed,
# favoring earlier players.
def baseline(nplayers, num_card_values, num_cards, trials, agent=None, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Determining baseline using learning SketchyPolicy agents."
    if sketch_list is None:
        sketch_list = [0.1 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    for i in range(nplayers):
        if agent is not None:
            if agent != i: continue
        print "Simulating agent",i,"..."
        game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],i,verbose=0)
        ppolicy = policy.LessStupidPolicy(game)
        apolicies = []
        for t in range(nplayers):
            apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
        game.setPolicies(apolicies)
        simulators.allsetsimulate(game,ppolicy.decision,numTrials=trials,verbose=verbose)
        print "Wins observed:",game.wins
        print "Agent in position",i,"has a win rate of ",str(float(game.wins[i])/sum(game.wins))
        game.resetWins()

# Acquires the win rate of a learning SketchyPolicy agent with sketchiness 0.5 and confidence 1
# in each of the nplayers positions. This agent can see the last play and will perfectly call BS
# on it. Formatting is the same as a call to baseline. Generally, the win rate for the oracle is above
# 90%.
def oracle(nplayers, num_card_values, num_cards, trials, agent=None, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Determining oracle using learning SketchyPolicy agents."
    if sketch_list is None:
        sketch_list = [0.1 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    for i in range(nplayers):
        if agent is not None:
            if agent != i: continue
        print "Simulating agent",i,"..."
        game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],i,verbose=0,oracle=True)
        ppolicy = policy.LessStupidPolicy(game)
        apolicies = []
        for t in range(nplayers):
            apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
        game.setPolicies(apolicies)
        simulators.allsetsimulate(game,ppolicy.decision,numTrials=trials,oracle=True,verbose=False)
        print "Wins observed:",game.wins
        print "Agent in position",i,"has a win rate of ",str(float(game.wins[i])/sum(game.wins))
        game.resetWins()

# Uses qlearning to create an agent against some adversaries. The adversaries will have random sketchiness and confidence
# unless lists are passed to the respective parameters. The algorithm learns for |learn_trials| iterations before being
# evaluated for |test_trials| iterations.
def qlearn_learn(nplayers,num_card_values,num_cards,agent,learn_trials,test_trials, featureExtractor = qlearn.snazzyFeatureExtractor, explorationProb = 0.2, maxIters = 1000, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Running qlearning as agent",agent,"."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=0)
    if sketch_list is None:
        sketch_list = [0.5 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
    game.setPolicies(apolicies)
    qlearning = qlearn.QLearningAlgorithm(game.actions,game.discount(),featureExtractor,explorationProb=explorationProb)
    print "Learning..."
    simulators.rlsimulate(game,qlearning,numTrials=learn_trials,verbose=verbose,maxIterations = maxIters)
    qlearning.explorationProb = 0
    game.resetWins()
    print "Learning complete. Now simulating tests..."
    simulators.rlsimulate(game,qlearning,numTrials=test_trials,verbose=verbose,maxIterations = maxIters)
    print "Wins observed:",game.wins
    print "Agent in position",agent,"has a win rate of",str(float(game.wins[agent])/sum(game.wins))
    return qlearning

def mb_learn(nplayers,num_card_values,num_cards,agent,learn_trials,test_trials, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Running qlearning as agent",agent,"."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=0)
    if sketch_list is None:
        sketch_list = [0.5 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
    game.setPolicies(apolicies)
    mb = model_based.ModelBasedAlgorithm(game.actions,game.discount())
    print "Learning..."
    simulators.rlsimulate(game,mb,numTrials=learn_trials,verbose=verbose)
    mb.explorationProb = 0
    game.resetWins()
    print "Learning complete. Now simulating tests..."
    simulators.rlsimulate(game,mb,numTrials=test_trials,verbose=verbose)
    print "Wins observed:",game.wins
    print "Agent in position",agent,"has a win rate of",str(float(game.wins[agent])/sum(game.wins))
    return mb

# This takes as input a built qlearning and tests it against a different set of adversary agents. Useful for figuring out
# how generally applicable a learned policy is against enemies that aren't exactly the same as those we learned against.
def qlearn_test(nplayers,num_card_values,num_cards,agent,trials,qlearning, sketch_list = None, confidence_list = None, learn_list = None, verbose=False):
    print "Testing qlearning as agent",agent,"."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=0)
    if sketch_list is None:
        sketch_list = [0.5 for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
    game.setPolicies(apolicies)
    qlearning.explorationProb = 0
    print "Simulating..."
    simulators.rlsimulate(game,qlearning,numTrials=trials,verbose=verbose)
    print "Wins observed:",game.wins
    print "Agent in position",agent,"has a win rate of",str(float(game.wins[agent])/sum(game.wins))

# Runs |trials| games of sketchy policies playing against one another. Ideally, the agent parameter should make no difference,
# but it is available for testing purposes (to ensure that it has no effect).
def allsketchy_test(nplayers, num_card_values, num_cards, trials, agent = 0, sketch_list = None, confidence_list = None, learn_list = None, verbose = False):
    print "Running an all-sketchy simulation."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=0)
    if sketch_list is None:
        sketch_list = [random.random()  for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
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

def human_test(nplayers, num_card_values, num_cards, agent, qlearnings = None, sketch_list = None, confidence_list = None, learn_list = None, verbose = False):
    print "Running a simulation with a human player."
    game = play_game.BSGame(nplayers,[num_cards for _ in range(num_card_values)],agent,verbose=1)
    if sketch_list is None:
        sketch_list = [random.random()  for _ in range(nplayers)]
    if confidence_list is None:
        confidence_list = [1 for _ in range(nplayers)]
    if learn_list is None:
        learn_list = [False for _ in range(nplayers)]
    print "Players have sketchiness",sketch_list
    print "Players have confidence",confidence_list
    apolicies = []
    for t in range(nplayers):
        if qlearnings is None or qlearnings[t] is None:
            apolicies.append(policy.SketchyPolicy(game,sketch_list[t],confidence=confidence_list[t],learn=learn_list[t]).decision)
        else:
            apolicies.append(qlearnings[t].getAction)
    game.setPolicies(apolicies)
    print "Simulating..."
    simulators.humansimulate(game)