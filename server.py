
import pickle

class server_list:
    """
    [
    ip,
    port,
    [channels]
    ]
    """

    def __init__(self):
        self.filename = "server_list.p"
        self.slist = []
        self.clist = []
        self.notify = []
        self.refresh()

    def save(self):
        with open(self.filename,"wb") as f:
            pickle.dump(self.slist,f)
        with open("notify.p", "wb") as f:
            pickle.dump(self.notify, f)
            print(self.notify)
        self.refresh()

    def refresh(self):
        with open(self.filename, "rb") as f:
            self.slist = pickle.load(f)
        with open("notify.p", "rb") as f:
            self.notify = pickle.load(f)
        self.clist = []
        for l in self.slist:
            for c in l[2]:
                self.clist.append([c,l[0],l[1]])

    def add_server(self, channel, ip, port):
        for i in self.clist:
            if i[0] == channel:
                return -1
        for l in range(len(self.slist)):
            if self.slist[l][0] == ip and self.slist[l][1] == port:
                self.slist[l][2].append(channel)
                print("add channel")
                break
            else:
                self.slist.append([ip,port,[channel]])
                print("add server")
                break
        if len(self.slist) == 0:
            self.slist.append([ip,port,[channel]])
            print("create new list")
        self.save()
        return 1

    def remove_server(self, channel):
        ip = ""
        for i in range(len(self.clist)):
            if self.clist[i][0] == channel:
                ip = self.clist[i][1]
        if ip == "":
            return -1
        for l in range(len(self.slist)):
            if ip == self.slist[l][0]:
                for c in range(len(self.slist[l][2])):
                    if channel == self.slist[l][2][c]:
                        del self.slist[l][2][c]
                        if len(self.slist[l][2]) == 0:
                            del self.slist[l]
                        self.save()
                        return 1
