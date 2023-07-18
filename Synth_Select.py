# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 00:53:48 2023

@author: rohan
"""

def normaldist(n,mu=0,var=1):
    from scipy.stats import norm
    return norm.rvs(size=n,loc=mu,scale=var)

def gammadist(n,alpha,beta,loc=0):
    from scipy.stats import gamma
    return gamma.rvs(a=alpha, size=n, loc=loc,scale=1/beta)

def expdist(n,lam,loc=0):
    from scipy.stats import expon
    return expon.rvs(scale=1/lam,loc=loc,size=n)

def poissondist(n,mu,loc=0):
    from scipy.stats import poisson
    return poisson.rvs(mu=mu, size=n,loc=loc)

def binomialdist(size,n,p,loc=0):
    #Each element in array is number of successes in n trials if each success had probability p
    from scipy.stats import binom
    return binom.rvs(n=n,p=p,size=size,loc=loc)

def bernoullidist(size,p,loc=0):
    from scipy.stats import bernoulli
    return bernoulli.rvs(size=size,p=p,loc=loc)


def load_dataset(name):
    '''
    Parameters
    ----------
    name : String
        The name of the dataset to load. Must be either of:
            1) '10_class_multicut',
            2) '4D_AND',
            3) '5_class_multicut',
            4) '5D_XOR',
            5) 'cone',
            6) 'double_spiral',
            7) 'hypersphere_3D',
            8) 'trig',
            9) 'y=x',
            10)'yinyang'
    Returns
    -------
    Pandas dataframe object with the loaded dataset.
    '''
    available_datasets={'10_class_multicut':'10Class Multicut.csv','4D_AND':'4D AND.csv',
                        '5_class_multicut':'5Class Multicut.csv','5D_XOR':'5D XOR.csv',
                        'cone':'Cone.csv','double_spiral':'Double Spiral.csv',
                        'hypersphere_3D':'Hypersphere 3D.csv','trig':'Trig.csv',
                        'y=x': 'y=x.csv','yinyang':'Yinyang.csv'}
    
    assert name in available_datasets
    
    import pandas as pd
    df=pd.read_csv("./Datasets/"+available_datasets[name])
    return df
    
def addIrrelevant(data,numIrrelevantCols=5,distributions=['normal','gamma','exponential']):
    '''
    Parameters
    ----------
    data : Pandas dataframe
        Dataframe to add the Irrelevant columns to.
    numIrrelevantCols : int, optional
        Number of irrelevant columns to add. The default is 5.
    distributions : list[distribution_names], optional
        distributions to use to make these irrelevant columns. The default is ['normal','gamma','exponential'].
        
        distribution_names must be one of:
        "normal","gamma","exponential"
        
    Returns
    -------
    df : Pandas dataframe
        Dataframe with the irrelevant columns added.
    '''
    import numpy as np
    size=len(data)
    df=data.copy()
    paramDomains={normaldist:[size,(-50,50),(0,10)],#n,mu,var
                  gammadist:[size,(0,50),(0,50),0],#n,alpha,beta,loc
                  expdist:[size,(0,1),0],#n,lam,loc
                  poissondist:[size,(0,50),0],#n,mu,loc
                  binomialdist:[size,(2,10),(0,1)],#size,n,p
                  bernoullidist:[size,(0,1),0]}#size,p,loc
    
    strToFunc={'normal':normaldist,'gamma':gammadist,'exponential':expdist,
               'poisson':poissondist,'binomial':binomialdist,'bernoulli':bernoullidist}
    
    #Domain for each parameter in each function - infinite domains restricted arbitrarily
    #Use: params will be randomized for each irrelevant column
    epsilon=1e-3 #Used to exclude lower bound
    
    numFeats=len(df.columns)-1
    for i in range(numIrrelevantCols):
        distfunc=strToFunc[np.random.choice(distributions,size=1)[0]]
        numFeats+=1
        params=[size]
        for prange in paramDomains[distfunc][1:]:
            if isinstance(prange,int): params.append(0)
            else: params.append(np.random.uniform(low=prange[0]+epsilon,high=prange[1],size=1)[0])
            
        df[f'F{numFeats}_Irr']=distfunc(*params)
        
    #Move target to the right most column
    target=df.Target
    df.drop('Target',axis=1,inplace=True)
    df['Target']=target
    return df

def addRedundant(df,numRedFeats=5):
    '''
    Parameters
    ----------
    df : Pandas dataframe
        Dataframe to add the Redundant columns to.
    numRedFeats : int
        Number of redundant features to add. The default is 5.

    Returns
    -------
    data : Pandas dataframe
        Dataframe with the redundant columns added.

    '''
    import numpy as np
    data=df.copy()
    colsToAugment=np.random.choice(data.columns[:-1],size=numRedFeats)
    count=0
    for col in colsToAugment:
        count+=1
        #Linear augmentation
        coef=np.random.randint(-50,51)
        offset=np.random.randint(-100,101)
        data[col+'_red_'+str(count)]=coef*data[col]+offset
    #Put target col at the end
    target=data['Target']
    data=data.drop('Target',axis=1)
    data['Target']=target
    return data

def addRedundantCat(data,numRedFeats=5):
    '''
    Parameters
    ----------
    data : Pandas dataframe
        Dataframe to add the Redundant columns to..
    numRedFeats : int
        Number of redundant features to add. The default is 5.

    Returns
    -------
    data : Pandas dataframe
        Dataframe with the redundant columns added.

    '''
    import numpy as np
    
    # Just negate the input
    colsToAugment=np.random.choice(data.columns[:-1],size=numRedFeats)
    count=0
    for col in colsToAugment:
        count+=1
        data[col+'_red_'+str(count)]=data[col].apply(lambda x:int(not(x)))
    #Put target col at the end
    target=data['Target']
    data=data.drop('Target',axis=1)
    data['Target']=target
    return data



def addIrrelevantCat(df,numIrrelevantCols=5,distributions=[normaldist,gammadist,expdist]):
    ''''
    Parameters
    ----------
    df : Pandas dataframe
        Dataframe to add the Irrelevant columns to.
    numIrrelevantCols : int, optional
        Number of irrelevant columns to add. The default is 5.
    distributions : list[distribution_names], optional
        distributions to use to make these irrelevant columns. The default is ['normal','gamma','exponential'].
        
        distribution_names must be one of:
        "normal","gamma","exponential"
        
    Returns
    -------
    df : Pandas dataframe
        Dataframe with the irrelevant columns added.
    '''
    import numpy as np
    import pandas as pd
    size=len(df)
    paramDomains={normaldist:[size,(-50,50),(0,10)],#n,mu,var
                  gammadist:[size,(0,50),(0,50),0],#n,alpha,beta,loc
                  expdist:[size,(0,1),0],#n,lam,loc
                  poissondist:[size,(0,50),0],#n,mu,loc
                  binomialdist:[size,(2,10),(0,1)],#size,n,p
                  bernoullidist:[size,(0,1),0]}#size,p,loc
    #Domain for each parameter in each function - infinite domains restricted arbitrarily
    #Use: params will be randomized for each irrelevant column
    epsilon=1e-3 #Used to exclude lower bound
    strToFunc={'normal':normaldist,'gamma':gammadist,'exponential':expdist,
               'poisson':poissondist,'binomial':binomialdist,'bernoulli':bernoullidist}
    
    
    def split(df, func=lambda x, y: x > y):
        #assert func.__code__.co_argcount == len(df.columns)
        #df_t = df.copy()
        res = df.apply(lambda x: func(*[x[c] for c in df.columns]), axis=1)
        return res
    
    numFeats=len(df.columns)-1
    for i in range(numIrrelevantCols):
        distfunc=strToFunc[np.random.choice(distributions,size=1)[0]]
        numFeats+=1
        params=[size]
        for prange in paramDomains[distfunc][1:]:
            if isinstance(prange,int): params.append(0)
            else: params.append(np.random.uniform(low=prange[0]+epsilon,high=prange[1],size=1)[0])
        
        res=distfunc(*params)
        df[f'F{numFeats}_Irr']=split(pd.DataFrame(res,columns=['x']),func=lambda x:int(x>res.mean()))
    
    #Move target to the right most column
    target=df.Target
    df.drop('Target',axis=1,inplace=True)
    df['Target']=target
    return df
