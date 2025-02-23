import numpy as np
import copy
import random
import pandas as pd
from data_reader import *
import time
import csv
def gt(X,p,op,m,n):
    omega=copy.deepcopy(op)
    S=[]
    start=np.zeros((m,n))
    while len(omega)!=0:
        f_min=10**10
        for k,l in omega:
            f=start[k,l]+p[k,l]
            if f<=f_min:
                f_min=f
                m_min=k
                l_min=l
        op_set = [[m_min,j] for i,j in omega if i==m_min and start[m_min,j]<=f_min]
        x_min=n-1
        for k,l in op_set:
            if x_min>=X[k].index(l):
                x_min=X[k].index(l)
                l_min=l
        S.append([m_min,l_min])
        start[m_min]=f_min
        for i in range(m):
            start[i,l_min]=f_min
        omega.remove([m_min,l_min])
    return S


def fitness_tbar(c_time,d,n):
    tardiness=[0]*n
    for i in range(n):
        tardiness[i]=max(0,c_time[i]-d[i])
    return np.mean(tardiness)


def get_c(s,p,m,n):
    job_ready=[0]*n
    machine_ready=[0]*m
    for j in range(n):
        for i in range(m):
            current_job=s[i][j] 
            current_machine=i
            start=max(job_ready[current_job],machine_ready[current_machine])
            process=p[i,j]
            finish=start+process
            job_ready[current_job]=finish
            machine_ready[current_machine]=finish
    return job_ready
       
def get_machine_schedule(S,m):
    s={i:[] for i in range(m)}
    for i,j in S:
        s[i].append(j)
    return s

def update_velocity(velocity,m,n,pop_size,w):
    for k in range(pop_size):
        for i in range(m):
            for j in range(n):
                r=random.uniform(0,1)
                if velocity[k][i][j]==1 and r>=w:
                    velocity[k][i][j]=0
    return velocity

def move_particle(particle,pbest_k,gbest,velocity_k,m,n,c1,c2):
    for i in range(m):
        l=random.randint(0,n-1)
        for j in range(n):
            r=random.uniform(0,1)
            if r<=c1:
                j1=particle[i][l]
                l_prime=pbest_k[i].index(l)
                j2=particle[i][l_prime]
                if velocity_k[i][j1]==0 and velocity_k[i][j2]==0 and j1!=j2:
                    particle[i][l]=j2
                    particle[i][l_prime]=j1
                    velocity_k[i][j1]=1
            elif r>c1 and r<=c1+c2:
                j1=particle[i][l]
                l_prime=gbest[i].index(l)
                j2=particle[i][l_prime]
                if velocity_k[i][j1]==0 and velocity_k[i][j2]==0 and j1!=j2:
                    particle[i][l]=j2
                    particle[i][l_prime]=j1
                    velocity_k[i][j1]=1
            l+=j
            if (l>n-1):   
                l=l-(n-1)
     
    return particle,velocity_k



def main():
    #number of jobs
    n=100
    #number of machines
    m=27
    #processing times

    p=processing_times(m,n)
    #due date
    d=due_date(n)

    pop_size=30
    #set the priority list randomly
    pop=[]
    #operations list
    op=[[i,j] for i in range(m) for j in range(n)]
    for _ in range(pop_size):
        X=[]
        for i in range(m):
            jobs=[j for j in range(n)]
            random.shuffle(jobs)
            X.append(jobs)
        pop.append(X)
    pop_fitness=[0]*pop_size
    pbest_fitness=[0]*pop_size
    pbest=[]
    #initial loop of the algorithm
    for i in range(len(pop)):
        schedule=gt(pop[i],p,op,m,n)
        s=get_machine_schedule(schedule,m)
        c_time=get_c(s,p,m,n)
        pop_fitness[i]=fitness_tbar(c_time,d,n)
        pbest.append(pop[i])
        pbest_fitness.append(pop_fitness[i])
    #set g best solution to best p_best
    gbest=pop[pop_fitness.index(min(pop_fitness))]
    max_iter=500
    velocity=[[[1]*n]*m]*pop_size
    w=.5
    c1=.5
    c2=.3
    #sort the pbest best to worst
    pbest = [x for _,x in sorted(zip(pbest_fitness,pbest))]
    #get gbest fitness:
    schedule=gt(gbest,p,op,m,n)
    s=get_machine_schedule(schedule,m)
    c_time=get_c(s,p,m,n)
    gbest_fitness=fitness_tbar(c_time,d,n)
    #main algorithm PSO:
    for _ in range(max_iter):
        print(_)
        velocity=update_velocity(velocity,m,n,pop_size,w)
        for k in range(pop_size):
            pop[k],velocity[k]=move_particle(pop[k],pbest[k],gbest,velocity[k],m,n,c1,c2)
            schedule=gt(pop[k],p,op,m,n)
            s=get_machine_schedule(schedule,m)
            c_time=get_c(s,p,m,n)
            pop_fitness[k]=fitness_tbar(c_time,d,n)
        if min(pop_fitness)<=gbest_fitness:
            pbest[-1]=gbest
            gbest=pop[pop_fitness.index(min(pop_fitness))]
        elif min(pop_fitness)<=pbest_fitness[-1]:
            the_same=0
            if min(pop_fitness)==gbest_fitness:
                gbest=pop[pop_fitness.index(min(pop_fitness))]
                the_same=1
            else:
                for l in range(pop_size):
                    if min(pop_fitness)==pbest_fitness[l]:
                        pbest[l]=pop[pop_fitness.index(min(pop_fitness))]
                        the_same=1
                        break
            if the_same==0:
                pbest[-1]==pop[pop_fitness.index(min(pop_fitness))]
    best_schedule=gt(gbest,p,op,m,n)
    best_s=get_machine_schedule(best_schedule,m)
    c_time=get_c(s,p,m,n)
    best_fitness=fitness_tbar(c_time,d,n)
    return best_s,best_fitness
if __name__=='__main__':
    start_time=time.time()
    best_schedule,best_fitness=main()
    with open('results.csv','w',newline='') as csvfile:
        writer=csv.writer(csvfile,delimiter=' ')
        writer.writerow([best_schedule,best_fitness])
    print(time.time()-start_time)