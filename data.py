
class StreamerData:

    def __init__(self):

        self.viewers = {}
        self.currentViewers = []

        self.authUsers = {}

    def loadViewerData(self, fileName="viewerData.csv"):

        try:
            with open( fileName, "a+" ) as dataFile:
                dataFile.seek(0)

                for line in dataFile:

                    parts = line.split( "," )

                    name = parts[0].strip()

                    userInfo = parts[1:]
                    for i in range( 0, len(userInfo) ):
                        try:
                            userInfo[i] = int( userInfo[i] )
                        except:
                            userInfo[i] = userInfo[i].strip()
                    self.viewers[name] = userInfo
            return 0
        except Exception as e:
            #print( "File \"{}\" could not be opened.".format( fileName ) )
            print( e )
            return 1

    def saveViewerData(self, fileName="viewerData.csv"):

        try:
            with open( fileName, "w" ) as dataFile:

                for viewer in self.viewers:

                    dataFile.write( viewer + "," + ",".join( str(x) for x in self.viewers[viewer] ) + "\n" )
        except Exception as e:
            #print( "File \"{}\" could not be opened.".format( fileName ) )
            print( e )

    def loadAuthUsers(self, fileName="authorizedUsers.csv"):

        try:
            with open( fileName, "a+" ) as dataFile:
                dataFile.seek(0)

                for line in dataFile:

                    parts = line.split( "," )

                    command = parts[0].strip()

                    users = parts[1:]
                    for i in range( 0, len(users) ):
                        users[i] = users[i].strip()
                    self.authUsers[command] = users
            return 0
        except Exception as e:
            #print( "File \"{}\" could not be opened.".format( fileName ) )
            print( e )
            return 1

    def saveAuthUsers(self, fileName="authorizedUsers.csv"):

        try:
            with open( fileName, "w" ) as dataFile:

                for command in self.authUsers:

                    dataFile.write( command + "," + ",".join( str(x) for x in self.authUsers[command] ) + "\n" )
        except Exception as e:
            #print( "File \"{}\" could not be opened.".format( fileName ) )
            print( e )

    def initialize(self, viewers ):

        self.currentViewers = viewers
        self.loadViewerData()
        for v in self.currentViewers:

            if v not in self.viewers:
                self.viewers[v] = [0]

        self.loadAuthUsers()

    def addAuthorizedUser(self, command, user ):

        if user not in self.authUsers[command]:
            self.authUsers[command].append( user )
            return True
        else:
            return True

    def isAuthorized(self, command, user ):

        if command in self.authUsers:
            if user in self.authUsers[command]:
                return True
            else:
                return False
        else:
            return False

    def save(self):

        self.saveViewerData()
        self.saveAuthUsers()
        return True

    def points( self, name ):

        return self.viewers[name][0]
