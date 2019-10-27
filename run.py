from deeppavlov import build_model, configs
model = build_model(configs.squad.squad_bert, download=True, load_trained=True)


import pyrebase

config = {
    "apiKey": "AIzaSyDpDm_HPVsWN0RPl12U8NDgK1-VnQJzXtg",
    "authDomain": "wbdb-44898.firebaseapp.com",
    "databaseURL": "https://wbdb-44898.firebaseio.com",
    "storageBucket": "wbdb-44898.appspot.com"
} 

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def stream_handler(post):
    # where it was added
    new_id = post["path"]

    # make sure it is a new question by checking the length of the added path
    parts = new_id.split('/')
    print('Parts: ' + str(parts)) 
    if len(parts) < 3 and parts[1] != '' and post["event"] == "put":
         data = post["data"]
         print('Data: ' + str(data))
         if data == None:
             return;
         # grab the name of the subject
         subject = db.child("tutorbot/session1/subject").get().val()

         # grab all the materials regarding the subject
         contexts = db.child("contexts/" + subject).get().val()
         # each contains image urls, clean and timed texts as matched with the audio of the lecture
         for key, value in contexts.items():
            # downloads related images from firebase storage
            image_names = value['pics']
            response, confidence = respond(value['text']['raw_text'], data['text'])
            timed_text = value['text']['times']

            if response != '':
                temp_output = {}
                # get the response to the question
                temp_output['response'] = response
                temp_output['confidence'] = confidence
                pic_url, match = get_pic_with_answer(timed_text, image_names, response[0])

                # get the related images if exists
                if pic_url != None:
                    true_url = firebase.storage().child(pic_url).get_url(token=None)
                    temp_output['url'] = true_url
                
                # has not been verified as a good answer
                temp_output['status'] = 'none'
                db.child("tutorbot/session1/questions/" + parts[1] + '/answers/').push(temp_output)


def respond(context, question):
    results =  model([context], [question])
    return results[0], results[2]
    #print(context + " " + question)
    #return "Response" 

    
def get_pic_with_answer(word_times, pics, answer):
    try:
        pic_url = None
        answer_split = answer.split(" ")
        idx = None
        start_time = None
        end_time = None
        match = False

        for i in range(len(word_times)):
            for j in range(len(answer_split)):
                if i + j < len(word_times):
                    if word_times[i + j][0] != answer_split[j]:
                        break
                else:
                    break
                idx = i
                start_time = int(word_times[i][1].split("-")[0])
                end_time = int(word_times[i + j][1].split("-")[1])
                if j == len(answer_split) - 1:
                    match = True
        
        if not match:
            return None, None

        pic_url = pics[0]
        start = int(pics[0].replace(".png","").split("-")[0])
        end = int(pics[0].replace(".png","").split("-")[1])
        max_overlap = min(end,end_time) - max(start,start_time)
        
        for pic in pics:
            start = int(pic.replace(".png","").split("-")[0])
            end = int(pic.replace(".png","").split("-")[1])
            overlap = min(end,end_time) - max(start,start_time)
            if overlap > max_overlap:
                pic_url = pic

        return pic_url, answer
    except:
        return None, None

# word_times = [("The","1572125510-1572125512"),("Cat","1572125512-1572125514"),("in","1572125514-1572125516"),("the","1572125518-1572125520"),("hat","1572125522-1572125524")]
# pics = ["1572125509-1572125517.pdf","1572125518-1572125520.pdf"]
# answer = "the hats"
# pic_url, answer = get_pic_with_answer(word_times, pics, answer)
# print(pic_url)
# print(answer)

my_stream = db.child("tutorbot/session1/questions").stream(stream_handler, None)

while True:
    temp = 1
