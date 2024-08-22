import model
import envi
import time
import numpy as np

reTrain = False
if reTrain:
    Q_ , _ ,pi,_ , _ = model.Q_learning(model.env)
    save_P = np.array(Q_)
    print(save_P)
    try:
        np.save('Parameters.npy',save_P)
    except:
        pass
else:
    Q = np.load('Parameters.npy',allow_pickle=True)
    pi = lambda s: np.argmax(Q, axis=1)[s]
state, terminal = model.env.reset(model.env.HEIGTH,model.env.WIDTH)
print("temrinal:",terminal)
lost_counter = 0

while True:
    while not terminal:
        action = pi(state)
        state , _ , terminal = model.env.step(action)
        time.sleep(.04)
        model.env.print_world(model.env.world,model.env.margin_X,model.env.margin_Y)
    lost_counter += 1
    #Q_ , _ ,pi,_ , _ = model.Q_learning(mo9,11)
        #print(len(observable_space[0]))9,11)
        #print(len(observable_space[0]))del.env, n_episodes = 3000 + 500*lost_counter)
    state, terminal = model.env.reset(model.env.HEIGTH,model.env.WIDTH)    
    time.sleep(.5)  