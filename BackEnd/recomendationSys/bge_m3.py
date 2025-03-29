# from FlagEmbedding import BGEM3FlagModel
import numpy as np
import datetime
# from transformers import AutoModel, AutoTokenizer

# Setting use_fp16 to True speeds up computation with a slight performance degradation
question_dict = {
    1 : "what kind of therapist you need ?" , 
    2: "How do you want to present at your sessions ?" , 
    3: "how old are you ?" , 
    4: "do you consider yourself religious?" , 
    5: "What are your expectations from your therapist? A therapist who... " , 
    6: "are there any preferences for your therapist?" , 
    7: "how do you prefer to communicate with your therapist?" , 
    8: "are you currently experiencing anxiety panic attacks or have any phobias?" , 
    9: "when was the last time you thought about suicide?" , 
    10: "do you have any problems or worries about intimacy? paramonia" , 
    11: "trouble concentrating on things like reading the newspaper or watching television?" }

#  disorders : depression , anxiety , Disruptive behaviour and dissocial disorders , eating disorders , 
#  Schizophrenia ,Egosim 
answere_patient_dict = {
    0: ["فرد" , "نوجوان" , "کودک" , "زوج" , "خانواده"] , 
    1: ["حضوری" , "محازی"] , 
    2: [ "کودک و نوجوان", "جوان", "بزرگسال" , "مسن"]  , 
    3: ["گوش دادن" , "کاوش گذشته" , "آموزش مهارت جدید" ,"اعتقادات" , "دادن تکلیف" , "مشخص کردن اهداف بیمار" , "چک کردن فعالانه بیمار" ] , 
    4: ["زن" , "مرد" , "" ] , 
    5: [ "غیر مدهبی" , "مذهبی" , "" ] , 
    # 7: ["مسن" , "جوان" , ""] , 
    6: ["پیام دادن" , "تماس تلفنی" , "ایمیل" , "نبود ارتباط" , ""] , 
    7: "پنیک،فوبیا،اضطراب" , 
    8: "خودکشی"  , 
    9: "پارانویا"  , 
    10: "عدم تمرکز" , 
    11: "افسردگی" , 
    12: "رفتار مخرب و اختلالات غیراجتماعی" , 
    13: "اختلال غذا خوردن" , 
    14: "اگوسیم"  , 
    15: "ADHD" 
}
doctor_answere_dict = {
    1: ["حضوری" , "مجازی"] , 
    2: [ "کودک " , "نوجوان", "جوان", "بزرگسال" , "مسن" , ""]  ,       
    3: ["گوش دادن" , "کاوش گذشته" , "آموزش مهارت جدید" ,"اعتقادات" , "دادن تکلیف" , "مشخص کردن اهداف بیمار" , "چک کردن فعالانه بیمار" ] , 
    4: [ "مذهبی" , "غیر مدهبی" ] , 
    5: ["فوبیا" , "اضطراب" , "خودکشی" ,"پارانویا" ,"افسردگی","اختلال غذا خوردن" ,"اگوسیم" , "ADHD","رفتار مخرب و اختلالات غیراجتماعی", "عدم تمرکز","پنیک" ] ,  
    6: ["پیام دادن" , "تماس تلفنی" , "ایمیل" , "نبود ارتباط" , ""] , 
    7: ["مرد" , "زن"] ,
    8: ["مسن" , "جوان" , ""] , 
}

def process_doctor_answeres(data , gender , birth_date ) : 
    final_text = ""
    try : 
        for key,value in data.items() : 
            if key in  [1 , 2 ,4, 6 ]:  
                final_text += doctor_answere_dict[key][int(value)]
                final_text += " "
            elif key == 3: 
                # print("in 4")
                buffer = data[key].split( ',')
                if len(buffer) > 0 : 
                    for i in buffer : 
                        if i in [str(j) for j in range(0 , 7 )] : 
                            final_text += doctor_answere_dict[key][int(i)]
                        else : 
                            final_text += i  
                        final_text += " " 
            elif key== 5: 
                buffer = data[key].split( ',')
                for i in buffer : 
                    if i in [str(j) for j in range(0 , 11)] : 
                        final_text += doctor_answere_dict[key][int(i)]
                    else : 
                        final_text += i 
                    final_text += " "

            else : 
                pass

        g = doctor_answere_dict[7][0] if gender== 'M' else doctor_answere_dict[7][1]
        final_text += g
        print("date   " , type(birth_date ) , " " ,birth_date.year )
        age = datetime.datetime.now().year - birth_date.year
        print(age)
        range_age = doctor_answere_dict[8][0] if age < 40 else  doctor_answere_dict[8][1]
        final_text += (" " + range_age)
        return final_text
    except Exception as e:
        print(e)    
        return None 


# Create the model and tokenizer

dir = 'model_cache'

url = "https://api.deepinfra.com/v1/openai/embeddings"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer tIuYaFZQRIh0cjOJlENCly2UBNL4zPPM"
}

def get_embeddings(sentences):
    import requests
    # Prepare the payload
    data = {
        "input": sentences,
        "model": "BAAI/bge-m3",
        "encoding_format": "float"
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    
    # Extract the embeddings
    embeddings = [item['embedding'] for item in response_data['data']]
    return embeddings




def getting_similarities( user_info , doctors_list , doctor_ids ) :     
    # model = BGEM3FlagModel('BAAI/bge-m3',  
    #                     use_fp16=False ) 
    
    if len ( doctors_list ) == 0 : 
        return []
    if not user_info : 
        return []
    
    # embeddings_1 = model.encode(user_info, 
    #                         batch_size=12, 
    #                         max_length=300, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
    #                         )['dense_vecs']

    embeddings_1 = get_embeddings(user_info)
    embeddings_1 = np.array(embeddings_1)
    embeddings_2 = get_embeddings(doctors_list)
    embeddings_2 = np.array(embeddings_2) 
    similarity = (embeddings_1 @ embeddings_2.T)
    ziped_list = list(zip(similarity, doctor_ids))
    ziped_list.sort(key=lambda x: x[0], reverse=True)
    return ziped_list

# ////////////////////

def process_patient_answeres(data ) : 
    # print( "--->   " , data )
    final_text = ""
    try : 
        for key,value in data.items() : 
            # print( " in process      and key is " , key , " and its type is " , type( key))
            if key in [0 ,1 ,2 , 4 , 5 , 6 ] :  
                # print("in 1 , 2 ")
                print( "key ****************** " , key)
                final_text += answere_patient_dict[key][int(value)]
                final_text += " "
            # elif key == 3 : 
            #     # print("in 3 ")
            #     if int(data[key]) < 20 : 
            #         final_text += answere_patient_dict[key][0]
            #     elif int(data[key]) < 36 : 
            #         final_text += answere_patient_dict[key][1]
            #     elif int(data[key]) < 65 : 
            #         final_text += answere_patient_dict[key][2]
            #     else : 
            #         final_text += answere_patient_dict[key][3]
            #     final_text += " "

            elif key == 3: 
                # print("in 4")
                buffer = data[key].split( ',')
                if len(buffer) > 0 : 
                    for i in buffer : 
                        if i in [str(j) for j in range(0 , 7 )] : 
                            final_text += answere_patient_dict[key][int(i)]
                        else : 
                            final_text += i  
                final_text += " " 

            elif key in [7, 9 ] and int(value) == 0 : 
                # print("in 7 , 9")
                final_text+= answere_patient_dict[key]
                final_text += " "
            elif key == 8 and int(data[key]) > 1:  
                # print("in 8")   
                final_text += answere_patient_dict[key]
                final_text += " "
            elif key == 10 and int(data[key]) ==2 : 
                # print("in 10")
                final_text += answere_patient_dict[key]
                final_text += " "
            elif key in [13 , 14 , 11 , 12] and int(data[key]) == 0:
                # print("in 11 , 12 , 13 , 14 " , key )
                final_text += answere_patient_dict[key]
                final_text += " "
            elif key == 15 and int(data[key]) > 6 : 
                # print("in 15 , key " , key )
                final_text += answere_patient_dict[key]
                final_text += " "
            else : 
                pass
        # print( "final text   " , final_text )
        return final_text
    except Exception as e : 
        print("exectpitsfj           " , e )
        return None 
            
        


# model = BGEM3FlagModel('BAAI/bge-m3', 
#                        use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation
# s1 = "جنسیت : زن"
# s1 += "\nبیماری افسردگی در خانواده من ارثی است. من دوره درمان اضطراب را گذرانده ام . "

# sentences_1 = [s1]
# sentences_2 = [". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند "  , "دکتر علی زاده . اکثر بیمار های ارثی ترجیج میدهم خانوم باشند "
#                ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند " , ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند "
#                ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند " , ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند "
#                ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند " , ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند " 
#                ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند " , ". من دکتر عبدی هستم. در زمینه بیماری های روان شناختی افسردگی کار میکنم .نظرم بر این است که این بیماری های ارئی هستند "]

# embeddings_1 = model.encode(sentences_1, 
#                             batch_size=12, 
#                             max_length=300, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
#                             )['dense_vecs']
# embeddings_2 = model.encode(sentences_2)['dense_vecs']
# similarity = embeddings_1 @ embeddings_2.T
# print(np.sort(similarity[0])[::-1])
