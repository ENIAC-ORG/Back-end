
def GlasserResults(data ) : 
    categories_score = {}
    categories_nums = {}
    for value in data.values() : 
        if value["category"] not in categories_score.keys() :     
            categories_score[ value["category"]] = value["res"] 
            categories_nums[ value["category"]] = 1
        else : 
            categories_score[ value["category"]] += value["res"] 
            categories_nums[ value["category"]] += 1
            
    for key in categories_nums.keys() : 
        categories_score[key] = round(( categories_score[key] /categories_nums[key]),2) 
    return categories_score 

def phq9Results(data) : 
    score = 0 
    if len (data) > 9 or len(data) ==0 : 
        return None
    for v in data.values(): 
        if v <0 or v > 3 : 
            return None
        score += v
    return score 
   
def GetMBTIresults(data, gender ) : 
    colomn1 = [ data[7*i + 1] for i in range(10)]   
    colomn2 = [ data[7*i + 2] for i in range(10)]   
    colomn3 = [ data[7*i + 3] for i in range(10)]   
    colomn4 = [ data[7*i + 4] for i in range(10)]   
    colomn5 = [ data[7*i + 5] for i in range(10)]   
    colomn6 = [ data[7*i + 6] for i in range(10)]   
    colomn7 = [ data[7*i + 7] for i in range(10)]   
    #  E , I 
    E = colomn1.count('a')*10
    I = colomn1.count('b')*10
    # S , N 
    S = (colomn2.count('a') + colomn3.count('a'))*5
    N = (colomn2.count('b') + colomn3.count('b'))*5
    # T , F
    T = (colomn4.count('a') + colomn5.count('a'))*5
    F = (colomn4.count('b') + colomn5.count('b'))*5
    # J , P 
    J = (colomn6.count('a') + colomn7.count('a'))*5
    P = (colomn6.count('b') + colomn7.count('b'))*5
    
    e_i =  'I'
    print('E ' ,E , 'I ' , I )
    if E > I : 
        e_i = 'E'

    s_n = 'N'
    if S > N : 
        s_n = 'S' 
    if T > F : 
        t_f = 'T'
    elif T == F and gender == 'M' : 
        t_f = 'T' 
    else : 
        t_f = 'F' 

    j_p =  'P'
    if J > P : 
        j_p = 'J'

    result = {
        'E' : E , 
        'I' : I , 
        'S' : S ,
        'N' : N ,
        'T' : T ,
        'F' : F ,
        'J' : J , 
        'P' : P , 
        'final' : e_i+s_n + t_f+ j_p
    }

    return result