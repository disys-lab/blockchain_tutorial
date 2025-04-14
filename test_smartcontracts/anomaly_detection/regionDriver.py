from random import randint
import numpy as np
import math
import pandas as pd
import scipy.stats as stats
from copy import copy
import pickle
import json

class regionDriver:

        def __init__(self,num_gens,t,mag,readFromFile=False,fileName=""):
            self.n = 1000
            self.t = t
            self.num_gens = num_gens
            self.mag = mag
            if not readFromFile:
                self.alpha,self.sigma_i,self.RL =  self.signalSimulator_Frequent(num_gens,t,mag)
            else:
                self.readProfile(fileName)
                if self.mag != mag:
                    print("ERROR loading profile from "+fileName)

            self.P_sigma_cap = {}
            self.P_sigma_cap[0] = 1-self.alpha
            self.P_sigma_cap[1] = self.alpha

        def writeProfile(self,fileName):
            regionProfile = {}
            regionProfile["n"] = self.n
            regionProfile["t"] = self.t
            regionProfile["num_gens"] = self.num_gens
            regionProfile["mag"] = self.mag
            regionProfile["alpha"] = self.alpha#pickle.dumps(self.alpha)
            regionProfile["sigma_i"] = pickle.dumps(self.sigma_i)
            regionProfile["RL"] = pickle.dumps(self.RL)

            with open(fileName, 'w') as outfile:
                json.dump(regionProfile, outfile)

        def readProfile(self,fileName):
            with open(fileName) as outfile:
                regionProfile = json.load(outfile)

            self.n = regionProfile["n"]
            self.t = regionProfile["t"]
            self.num_gens = regionProfile["num_gens"]
            self.mag = regionProfile["mag"]
            self.alpha = regionProfile["alpha"]
            self.sigma_i = pickle.loads(regionProfile["sigma_i"])
            self.RL = pickle.loads(regionProfile["RL"])
            self.P_sigma_cap = {}
            self.P_sigma_cap[0] = 1-self.alpha
            self.P_sigma_cap[1] = self.alpha



        def testReturnVal(self,rank):
            return rank

        def returnFirstSigmaI(self):
            for i in range(self.n):
                if self.sigma_i[i]==1:
                    return i

        def signalSimulator_Frequent(self,p,t,mag):
            alpha=0.005
            rl=200
            temp=0
            sigma=np.zeros(1000)
            RL=np.zeros(1000)
            p=p-1
            # if p<0:
#               return(alpha,sigma,RL)
            if p <= 0:
                p=1
            m=mag
            bias=1
            n=1000
            I=np.diagflat(np.repeat(1, p+1)).astype(float)
            A=np.diagflat(np.repeat(1, p+1)).astype(float)
            B=np.diagflat(np.repeat(1, p+1)).astype(float)
            C=np.diagflat(np.repeat(1, p+1)).astype(float)
            Q=np.diagflat(np.repeat(1, p+1)).astype(float)
            A[0,0:2]=[0.2,0.8]
            A[p,0:2]=[0.1,-0.1]
            A[p,p] = 0.1
            #print(A)
            R=0.1*I
            for i in range(0,p+1):
              Q[i,]=pow(0.5,np.abs(i-np.arange(p+1)))
            # U=np.diagflat(np.repeat(1, p)).astype(float)
            # W=np.diagflat(np.repeat(1, p)).astype(float)
            # z1=A[0:p,0:p] + np.dot(np.dot(np.dot(B[0:p,0:p],np.linalg.inv(U)), np.transpose(B[0:p,0:p])),np.transpose(np.linalg.inv(A[0:p,0:p])),W)
            # z2=- np.dot(np.dot(B[0:p,0:p],np.transpose(B[0:p,0:p])), np.transpose(np.linalg.inv(A[0:p,0:p])))

            # z3=-np.dot(np.transpose(np.linalg.inv(A[0:p,0:p])),W)
            # z4=np.transpose(np.linalg.inv(A[0:p,0:p]))
            # Z1=np.concatenate((np.concatenate((z1,z2),axis=0),np.concatenate((z3,z4),axis=0)),axis=1)
            # w,Z=np.linalg.eig(Z1)
            # Z=Z[:,p:]

            L = np.diagflat(np.repeat(-0.618034, p)).astype(float)

            # L=-solve(t(B[-p,-p])%*%S%*%B[-p,-p]+U)%*%t(B[-p,-p])%*%S%*%A[-p,-p]

            X=np.zeros((n+1,p+1))
            X_hat=np.zeros((n+1,p+1))
            Y=np.zeros((n,p+1))
            Y1=np.zeros((n,p+1))
            Y_hat=np.zeros((n,p+1))
            Y1_hat=np.zeros((n,p+1))
            y_hat=np.zeros(n)
            y1_hat=np.zeros(n)
            X[0,:] = np.random.multivariate_normal(np.zeros(p+1),I,1)
            P1=np.diagflat(np.repeat(1, p+1)).astype(float)
            X1=np.zeros(p+1)
            w=np.random.multivariate_normal(np.zeros(p+1),Q,n)
            v=np.random.multivariate_normal(np.zeros(p+1),R,n)

            for i in range(0,n):
                Y[i,] = np.dot(C,X[i,:])+v[i,:]
                y = copy(Y[i,:])
                Y_hat[i,:] = np.dot(C,X1)
                K = np.dot(P1,np.linalg.inv(P1+R))
                X0 = X1 + np.dot(K,(y-X1))
                P0=P1-np.dot(K,P1)
                X_hat[i,]=copy(X0)
                u=np.zeros(p+1)
                u[0:p]=np.dot(L,X0[0:p])
                X[i+1,:]=np.dot(A,X[i,])+np.dot(B,u)+w[i,:]
                P1=np.dot(np.dot(A,P0),np.transpose(A))+Q
                X1=np.dot(A,X0)+np.dot(B,u)

            w=np.random.multivariate_normal(np.zeros(p+1),Q,n)
            v=np.random.multivariate_normal(np.zeros(p+1),R,n)

            X[0,:]=copy(X[n,:])
            for i in range(0,n):
                Y1[i,] = np.dot(C,X[i,:])+v[i,:]
                y = copy(Y1[i,:])
                y[0:p] = copy(Y[i,0:p])
                Y1_hat[i,:] = np.dot(C,X1)
                K = np.dot(P1,np.linalg.inv(P1+R))
                X0 = X1 + np.dot(K,(y-X1))
                P0=P1-np.dot(K,P1)
                X_hat[i,]=copy(X0)
                u=np.zeros(p+1)
                u[0:p]=np.dot(L,X0[0:p])
                P1=np.dot(np.dot(A,P0),np.transpose(A))+Q
                X1=np.dot(A,X0)+np.dot(B,u)
                u[1]=u[1]+m
                X[i+1,:]=np.dot(A,X[i,])+np.dot(B,u)+w[i,:]

            Y2 = np.concatenate((Y[:,0:p],Y1[:,p:]),axis=1)
            y=np.concatenate((Y,Y2),axis=0)
            res = y-np.concatenate((Y_hat,Y1_hat),axis=0)
            #print(np.quantile(res[:n,p:],0.998))
            #result=(res[(n-t):,p:]< -2.4)+(res[(n-t):,p:]>2.4)
            #alpha=0.1
            result=(res[(n-t):,p:]< -3.1)+(res[(n-t):,p:]>3.1)
            RL=np.zeros(len(result))
            for i in range(0,len(result)):
                temp=temp+1
                # if sum>0:
                #     rl=temp
                if result[i]==1:
                    rl=temp
                    temp=0

                RL[i] = rl

            #alpha=0.005
            return (alpha,result,RL)

        def signalSimulator(self,p,t,mag):
            p=p-1 #no of generators
            m=mag #magnitude of attack(10,20)

            '''
            mag has to be positive
            if i increase mag, then it is detected sooner
            when its 10, the avg run length is 6
            when its 2, the avg run length is 16
            t is the time when the attack starts.
            after t is when the attack is going to be detected subject to mag
            '''
            bias=1
            n=1000
            I=np.diagflat(np.repeat(1, p+1)).astype(float)
            A=np.diagflat(np.repeat(1, p+1)).astype(float)
            B=np.diagflat(np.repeat(1, p+1)).astype(float)
            C=np.diagflat(np.repeat(1, p+1)).astype(float)
            Q=np.diagflat(np.repeat(1, p+1)).astype(float)
            A[p,p] = 0.1
            R=0.1*I
            for i in range(0,p+1):
              Q[i,]=pow(0.5,np.abs(i-np.arange(p+1)))
            # U=np.diagflat(np.repeat(1, p)).astype(float)
            # W=np.diagflat(np.repeat(1, p)).astype(float)
            # z1=A[0:p,0:p] + np.dot(np.dot(np.dot(B[0:p,0:p],np.linalg.inv(U)), np.transpose(B[0:p,0:p])),np.transpose(np.linalg.inv(A[0:p,0:p])),W)
            # z2=- np.dot(np.dot(B[0:p,0:p],np.transpose(B[0:p,0:p])), np.transpose(np.linalg.inv(A[0:p,0:p])))

            # z3=-np.dot(np.transpose(np.linalg.inv(A[0:p,0:p])),W)
            # z4=np.transpose(np.linalg.inv(A[0:p,0:p]))
            # Z1=np.concatenate((np.concatenate((z1,z2),axis=0),np.concatenate((z3,z4),axis=0)),axis=1)
            # w,Z=np.linalg.eig(Z1)
            # Z=Z[:,p:]

            L = np.diagflat(np.repeat(-0.618034, p)).astype(float)

            # L=-solve(t(B[-p,-p])%*%S%*%B[-p,-p]+U)%*%t(B[-p,-p])%*%S%*%A[-p,-p]

            X=np.zeros((n+1,p+1))
            X_hat=np.zeros((n+1,p+1))
            Y=np.zeros((n,p+1))
            Y1=np.zeros((n,p+1))
            Y_hat=np.zeros((n,p+1))
            Y1_hat=np.zeros((n,p+1))
            y_hat=np.zeros(n)
            y1_hat=np.zeros(n)
            X[0,:] = np.random.multivariate_normal(np.zeros(p+1),I,1)
            P1=np.diagflat(np.repeat(1, p+1)).astype(float)
            X1=np.zeros(p+1)
            w=np.random.multivariate_normal(np.zeros(p+1),Q,n)
            v=np.random.multivariate_normal(np.zeros(p+1),R,n)

            for i in range(0,n):
                Y[i,] = np.dot(C,X[i,:])+v[i,:]
                y = copy(Y[i,:])
                Y_hat[i,:] = np.dot(C,X1)
                K = np.dot(P1,np.linalg.inv(P1+R))
                X0 = X1 + np.dot(K,(y-X1))
                P0=P1-np.dot(K,P1)
                X_hat[i,]=copy(X0)
                u=np.zeros(p+1)
                u[0:p]=np.dot(L,X0[0:p])
                X[i+1,:]=np.dot(A,X[i,])+np.dot(B,u)+w[i,:]
                P1=np.dot(np.dot(A,P0),np.transpose(A))+Q
                X1=np.dot(A,X0)+np.dot(B,u)

            w=np.random.multivariate_normal(np.zeros(p+1),Q,n)
            v=np.random.multivariate_normal(np.zeros(p+1),R,n)

            X[0,:]=copy(X[n,:])
            for i in range(0,n):
                Y1[i,] = np.dot(C,X[i,:])+v[i,:]
                y = copy(Y1[i,:])
                y[0:p] = copy(Y[i,0:p])
                Y1_hat[i,:] = np.dot(C,X1)
                K = np.dot(P1,np.linalg.inv(P1+R))
                X0 = X1 + np.dot(K,(y-X1))
                P0=P1-np.dot(K,P1)
                X_hat[i,]=copy(X0)
                u=np.zeros(p+1)
                u[0:p]=np.dot(L,X0[0:p])
                P1=np.dot(np.dot(A,P0),np.transpose(A))+Q
                X1=np.dot(A,X0)+np.dot(B,u)
                u[1]=u[1]+m
                X[i+1,:]=np.dot(A,X[i,])+np.dot(B,u)+w[i,:]

            Y2 = np.concatenate((Y[:,0:p],Y1[:,p:]),axis=1)
            y=np.concatenate((Y,Y2),axis=0)

            eig_val,eig_vec=np.linalg.eig(np.cov(np.transpose(y[0:100,:])))
            PCy = np.dot(y,eig_vec)
            for i in range(0,p+1):
                PCy[:,i]=PCy[:,i]/math.sqrt(eig_val[i])
            Testy=(PCy**2).sum(axis=1)

            # result=(Testy[(n-t):]<stats.chi2.ppf(0.0022,df=p))+(Testy[(n-t):(2*n)]>stats.chi2.ppf(0.9978,df=p))
            # rl=100
            # alpha=0.005

            result=(Testy[(n-t):]<stats.chi2.ppf(0.01,df=p))+(Testy[(n-t):(2*n)]>stats.chi2.ppf(0.99,df=p))
            rl=25#50
            alpha=0.02

            temp=0
            RL=np.zeros(len(result))
            for i in range(0,len(result)):
                temp=temp+1
                if result[i]==1:
                    rl=temp
                    temp=0
                RL[i] = rl
            #alpha=0.02
            return (alpha,result,RL)

        # def pSigmaI(self,alpha,beta,sigma_i,P_sigma_cap):
        #     P_sigma_i = {}
        #     P_sigma_i[0]=(1-alpha)*P_sigma_cap[0]+(1-beta)*P_sigma_cap[1]
        #     P_sigma_i[1]=(alpha)*P_sigma_cap[0]+(beta)*P_sigma_cap[1]
        #     return P_sigma_i
            #pass

        def pSigmaI(self,alpha,sigma_i,P_sigma_cap,t):
            a_i = 0
            b_i = 0
            beta = 1/float(self.RL[t]+1e-2)
            if sigma_i == 0:
                a_i = (1-alpha)*P_sigma_cap[0]
                b_i = (1-beta)*P_sigma_cap[1]
            else:
                a_i = (alpha)*P_sigma_cap[0]
                b_i = (beta)*P_sigma_cap[1]
            #print b_i,a_i

            # if a_i<0.01:
            #     a_i=0.01
            # if a_i>0.99:
            #     a_i=0.99
            #
            # if b_i<0.01:
            #     b_i=0.01
            # if b_i>0.99:
            #     b_i=0.99

            return a_i,b_i,(a_i+b_i)

        def updatePrior(self,a_i,b_i):
            self.P_sigma_cap[0] = float(a_i)/(a_i+b_i)
            self.P_sigma_cap[1] = float(b_i)/(a_i+b_i)
            #pass
