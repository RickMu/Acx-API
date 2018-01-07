from repository.acx_repo import AcxDB

import datetime

def fixTime(data, collection):
    i =0
    for elem in data:
        i+=1
        if elem['created_at'][-1] == "Z":
            string = elem['created_at'][:-4]
            format = '%Y-%m-%dT%H:%M'
            d = datetime.datetime.strptime(string, format) + datetime.timedelta(hours=11)
            d = d.isoformat() + "+11:00"
            elem['created_at'] = d

            collection.update(elem['id'],{'created_at':d})
        if(i%10000==0):
            print(i)
    return data

if __name__ == "__main__":

    db = AcxDB()
    for m in db.getRepo.keys():
        collection = db.getRepository(m)[0]
        print("update: "+ str(m))
        cursor = list(collection.findAll())
        print("Length: = "+ str(len(cursor)))
        fixTime(cursor,collection)




