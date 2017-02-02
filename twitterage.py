#!/usr/bin/env python

import os.path
import shelve
import logging
import logging.handlers
import time
import datetime
import twitter
import copy

"""
Keeps an agenda of messages to be send out according to the dates.

The agenda is a dictionary of message id's with:
    * Start time of the event: YYYYMMDD[HHMM]     start
    * Message                                     message
    * Posted by                                   sender
Possibly more added later.

It will import tagenda.py and expects an oauth dictionary in it with the credentials like:
    oauth = dict(
        consumer_key='XXXXXXXXXXXXXXXXXXX',
        consumer_secret='YYYYYYYYYYYYYYYYYYYYYY',
        access_token_key='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
        access_token_secret='ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')

Agenda items can be managed using direct twitter messages from chosen twitter accounts.
"""

class InfoFilter(logging.Filter):
    """
    Logging filter that allows everything INFO.
    """
    def filter(self, rec):
        return rec.levelno == logging.INFO


class WarnFilter(logging.Filter):
    """
    Logging filter that allows everything WARN or worse.
    """
    def filter(self, rec):
        return rec.levelno >= logging.WARN


class TwitterException(Exception):
    """
    Thown when there is a problem tweeting.
    """
    pass


class DummyTwitterAPI(object):
    """
    Only used for testing: implements a dummy subset of the twitter API.
    """

    dm = [
            twitter.DirectMessage(id = 1234,
                                  sender_id = 12345,
                                  sender_screen_name = "Tester",
                                  text = "!Going onto the wild."),
            twitter.DirectMessage(id = 1235,
                                  sender_id = 12345,
                                  sender_screen_name = "Tester",
                                  text = "2013-08-31 Nationaal kampioenschap Engelse grasparkieten, Duffel (org. BGC A'pen)"),
            twitter.DirectMessage(id = 1236,
                                  sender_id = 12346,
                                  sender_screen_name = "Monitor",
                                  text = "?1"),
            twitter.DirectMessage(id = 1237,
                                  sender_id = 12346,
                                  sender_screen_name = "Monitor",
                                  text = "U 2013-08-31 Belgisch kampioenschap Engelse grasparkieten, O.L.Vrouwenlaan 1, 2570 Duffel (org. BGC A'pen)\nNIEUW: Ook kleurgrasparkieten!"),
            twitter.DirectMessage(id = 1238,
                                  sender_id = 12345,
                                  sender_screen_name = "Tester",
                                  text = "2013-08-31 07:30 tot 10:30 Inkooing Belgisch kampioenschap Engelse grasparkieten, O.L.Vrouwenlaan 1, 2570 Duffel"),
            twitter.DirectMessage(id = 1239,
                                  sender_id = 12345,
                                  sender_screen_name = "Tester",
                                  text = "%04d-%02d-%02d Test agenda item" % (datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day))
         ]

    def __init__(self, dm = None):
        if dm != None:
            self.dm = dm

    def VerifyCredentials(self):
        return "Logged into DummyTwitterAPI."


    def PostUpdate(self, **kwargs):
        """
        Tweet a message (emtpy)
        """
        logging.getLogger(__name__).debug("Post tweet: %s" % (kwargs))


    def GetDirectMessages(self, **kwargs):
        """
        Fetch the direct messages (returs self.dm)
        """
        logging.getLogger(__name__).debug("Getting direct messages: %s..." % (kwargs))
        logging.getLogger(__name__).debug("Found %s direct messages" % (len(self.dm)))
        return self.dm


    def DestroyDirectMessage(self, **kwargs):
        """
        Removes the direct message (empty)
        """
        logging.getLogger(__name__).debug("Delete direct message: %s" % (kwargs["id"]))


    def PostDirectMessage(self, **kwargs):
        """
        Posts a direct message (emtpy)
        """
        logging.getLogger(__name__).debug("Post direct message: %s" % (kwargs))


class TwitterAgenda(object):
    """
    The TwitterAgenda class sends regular tweets from the agenda.

    Entries can be added to the agenda via direct messages from selected accounts.

    The dictionary agenda containing the agenda entries. It is compatible with a shelve.
    The keys of this dictionary is the agendaId, a string of a natural number.
    The first entry is "0" and is not an agenda entry but used for other configuration:
        "0": {
            "timestamp": {
                "YYYYMMDD[HHMM]": list of the relevant agendaId's
                ...
            }
            "nextid": next free agendaId (string of a natural number)
            "last execution": yyyymmddhhmm of the last time the agenda was checked and action taken.

    A real agenda entry is like:
        "1": {
            "start": "YYYYMMDD[HHMM]"
            "message": message text
            "sender": who entered the agenda entry (like @twitteruser)
    """

    api = None

    agenda = {}

    # TODO: Short term: read it from a file
    #       Long term: using twitter lists for this?
    dmSetting = {
                    "@twitter": {"autz": "crud",
                                   "name": "Admin 1"},
                }

    @staticmethod
    def formatAgendaItem(agendaentry):
        """
        Formats an agenda entry into something readable for the enduser.

        It makes sure the result is 140 characters max.
        """
        # TODO: replace timestamp with 'Vandaag HH:MM' of 'Morgen HH:MM'.
        starttime = agendaentry['start']
        year = int(starttime[0:4])
        month = int(starttime[4:6])
        day = int(starttime[6:8])
        thetime = (datetime.date(year, month, day).strftime("%d %b '%y"))
        if len(starttime) == 12:
            hour = int(starttime[8:10])
            minute = int(starttime[10:12])
            thetime = (datetime.datetime(year, month, day, hour, minute).strftime("%d %b '%y om %H:%M"))
        text = "%s %s" % (thetime, agendaentry['message'])
        fulltext = "%s (%s)" % (text, agendaentry['sender'])
        # Breaking it down to 140 characters
        if (len(fulltext) > 140):
            fulltext = text[:140]
        return fulltext


    @staticmethod
    def parseAgendaItem(agendaentry, sender):
        """
        Parses the direct message and returns an agenda entry.

        The sender is the sender of the direct message.
        The start time of the agenda entry is parsed from the beginning of the message:
            YYYY-MM-DD HH:MM or
            YYYY-MM-DD
        The rest is the message.
        """
        entry = {}
        try:
            # YYYY-MM-DD HH:MM
            thetime = datetime.datetime.strptime(agendaentry[:16], "%Y-%m-%d %H:%M")
            timestamp = thetime.strftime("%Y%m%d%H%M")
            text = agendaentry[16:].strip()
        except:
            # YYYY-MM-DD
            thetime = datetime.datetime.strptime(agendaentry[:10], "%Y-%m-%d")
            timestamp = thetime.strftime("%Y%m%d")
            text = agendaentry[10:].strip()
        entry['start'] = timestamp
        entry['sender'] = "@%s" % (sender)
        entry['message'] = text
        return entry


    def __init__(self, agenda, api):
        """
        Initializes the class with an agenda and twitter api.

        The first argument is the agenda: This can a simple dictionary or a shelve.
        The second argument is a Twitter Api instance.
        """
        self.agenda = agenda
        self.api = api


    def loadAdmins(self):
        """
        UNDER CONSTRUCTION: This should become a function to extract the admins from a lists.

        Getting the twitter users from a list is not yet supported in the Twitter Api.
        """
        pass


    def __silentlyPostDirectMessage(self, **kwargs):
        try:
            self.api.PostDirectMessage(**kwargs)
        except:
            # Just logging it.
            logging.getLogger(__name__).error("Could not send Direct Message: %s." % (kwargs), exc_info = 1)


    def __addItem(self, zero, message, agendaId, agendaEntry):
        """
        Adds an agenda entry.

        Parameters:
            zero: copy of agenda["O"]
            message: direct message from where this entry is created/modified.
            agendaId: ID code for the entry (key for agenda dictionary)
            agendaEntry: agenda entry (value for agenda dictionary)

        It will make sure agenda["0"]["timestamp"] is also updated.
        """
        self.agenda[agendaId] = agendaEntry
        zero["timestamp"][agendaEntry["start"]].append(agendaId)
        self.agenda["0"] = zero
        logging.getLogger(__name__).info("Added agenda entry %s by %s via Direct Message: %s." % (agendaId, message.sender_screen_name, agendaEntry))
        # Notifying the poster (with ID for future reference)
        self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda item %s toegevoegd." % (agendaId))

    
    def doDirectMessages(self):
        """
        Read all open direct messages and act on them.

        Format of the messages:
            Adding messages to the agenda:
                YYYY-MM-DD <MESSAGE>
                YYYY-MM-DD HH:MM <MESSAGE>
            Querying a message in the agenda:
                ?<MESSAGEID>
            Updating/deleting/adding(forced) messages from the agenda:
                U<MESSAGEID> YYYY-MM-DD <MESSAGE>
                U<MESSAGEID> YYYY-MM-DD HH:MM <MESSAGE>
                D<MESSAGEID> YYYY-MM-DD <MESSAGE>
                D<MESSAGEID> YYYY-MM-DD HH:MM <MESSAGE>
                C<MESSAGEID> YYYY-MM-DD <MESSAGE>
                C<MESSAGEID> YYYY-MM-DD HH:MM <MESSAGE>
            Tweeting a message immediatly (does not involve the agenda):
                !MESSAGE
                ! MESSAGE
        """
        # Some initializing
        if "0" not in self.agenda:
            self.agenda["0"] = {"nextid": 1}
        # Read direct messages
        # TODO: !!!"lastidprocessed" is not yet implemented -- not sure if we need it !!!
        if "lastidprocessed" in self.agenda["0"]:
            # Get the messages from Twitter and reverse the order:
            #   Twitter will put the most recent first and we need them in chronological order.
            # TODO: What if 200 messages are returned, should I look for the rest as well?
            messages = self.api.GetDirectMessages(since_id = self.agenda["0"]['lastidprocessed'], count = 200)[::1]
        else:
            # Get the messages from Twitter and reverse the order:
            #   Twitter will put the most recent first and we need them in chronological order.
            # TODO: What if 200 messages are returned, should I look for the rest as well?
            messages = self.api.GetDirectMessages(count = 200)[::1]

        # Do something with entities.hashtags/urls/user_mensions
        errors = {}
        for message in messages:
            logging.getLogger(__name__).debug("Processing direct message %s" % (message))
            if "@%s" % message.sender_screen_name in self.dmSetting:
                # Authorized!
                preParseMessage = message.text
                # Needs urllib.unquote?

                if len(preParseMessage) == 0:
                    # Reply that it does not exist
                    logging.getLogger(__name__).warn("Empty Direct Message was send by %s." % (message.sender_screen_name))
                    # NOT REPLYING TO SOMETHING EMPTY # self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Je hebt een lege Direct Message gestuurd." % (agendaId))
                if preParseMessage[0] == "!":
                    # Tweet immediatly
                    # Message = "message (@sender)"
                    status = "%s (@%s)" % (preParseMessage[1:].strip(), message.sender_screen_name)
                    logging.getLogger(__name__).debug("Request for tweet: %s" % (status))
                    # limit to 140 characters: first drop the sender, next just cut.
                    if len(status) > 140:
                        status = preParseMessage[1:].strip()
                    status = status[:140]
                    # status = urllib.quote(status)
                    self.api.PostUpdate(status = status)
                    logging.getLogger(__name__).info("Tweeted on request of %s via Direct Message: %s" % (message.sender_screen_name, status))
                elif preParseMessage[0] == "?":
                    # Querying an entry in the agenda
                    agendaId = preParseMessage[1:].strip().encode("UTF-8")
                    logging.getLogger(__name__).debug("Request for info on agenda entry %s by %s." % (agendaId, message.sender_screen_name))
                    if agendaId == "" or agendaId == "0":
			# Query for all possible agendaId (sorted and skipping the first on "0" which isn't a real one)
			text = ",".join(sorted(agenda)[1:])
			logging.getLogger(__name__).info("Query agenda entries by %s via Direct Message: %s." % (message.sender_screen_name, text))
			text = text[-140:]
			self.__silentlyPostDirectMessage(user_id = message.sender_id, text = text)
                    elif agendaId in self.agenda:
                        # Found it, reply it
                        text = TwitterAgenda.formatAgendaItem(agenda[agendaId])
                        logging.getLogger(__name__).info("Query on agenda entry %s by %s via Direct Message: %s." % (agendaId, message.sender_screen_name, text))
                        self.__silentlyPostDirectMessage(user_id = message.sender_id, text = text)
                    else:
                        # Reply that it does not exist
                        logging.getLogger(__name__).warn("Agenda entry %s not found. Requested by %s via Direct Message." % (agendaId, message.sender_screen_name))
                        self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id %s onbekend." % (agendaId))
                elif preParseMessage[0].upper() == "U":
                    # Querying an entry in the agenda
                    logging.getLogger(__name__).debug("Request for updating agenda entry %s by %s" % (preParseMessage[1:], message.sender_screen_name))
                    temp = preParseMessage[1:].split()
                    if len(temp) > 0:
                        agendaId = temp[0]
                        preParseMessage = " ".join(temp[1:])
                        if agendaId == "0":
                            logging.getLogger(__name__).warn("Agenda entry 0 is not modifyable. Requested by %s via Direct Message." % (message.sender_screen_name))
                            self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id 0 kan niet aangepast worden.")
                        elif agendaId in self.agenda:
                            # Found it, modifying it
                            try:
                                # Parsing it
                                agendaEntry = self.parseAgendaItem(preParseMessage[1:].strip(), message.sender_screen_name)
                                self.agenda[agendaId] = agendaEntry
                                logging.getLogger(__name__).info("Updated agenda entry %s by %s via Direct Message: %s." % (agendaId, message.sender_screen_name, agendaEntry))
                            except Exception as err:
                                logging.getLogger(__name__).warn("Could not format agenda entry %s by %s via Direct Message." % (preParseMessage, message.sender_screen_name))
                                self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Er is een fout opgetreden: slecht formaat boodschap.")
                        else:
                            # Reply that it does not exist
                            logging.getLogger(__name__).warn("Agenda entry %s not found. Requested by %s via Direct Message." % (agendaId, message.sender_screen_name))
                            self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id %s onbekend." % (agendaId))
                    else:
                        # Reply that it does not exist
                        logging.getLogger(__name__).warn("No agenda entry specified. Requested by %s via Direct Message." % (message.sender_screen_name))
                        # NOT REPLYING TO SOMETHING EMPTY # self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Geen agenda id vermeld.")
                elif preParseMessage[0].upper() == "D":
                    # Querying an entry in the agenda
                    temp = preParseMessage[1:].split()
                    if len(temp) > 0:
                        agendaId = temp[0].encode('utf-8')
                        logging.getLogger(__name__).debug("Request for deleting agenda entry %s by %s." % (agendaId, message.sender_screen_name))
                        if agendaId == "0":
                            logging.getLogger(__name__).warn("Agenda entry 0 is not deletable. Requested by %s via Direct Message." % (message.sender_screen_name))
                            self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id 0 kan niet aangepast worden.")
                        else:
                            try:
                                # Trying to deleting it
                                del self.agenda[agendaId]
                                logging.getLogger(__name__).info("Agenda entry %s deleted by %s via Direct Message." % (agendaId, message.sender_screen_name))
                                self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id %s is verwijderd." % (agendaId))
                            except KeyError:
                                # Reply that it does not exist
                                logging.getLogger(__name__).warn("Agenda entry %s not found. Requested by %s via Direct Message." % (agendaId, message.sender_screen_name))
                                self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Agenda id %s onbekend." % (agendaId))
                    else:
                        # Reply that it does not exist
                        logging.getLogger(__name__).warn("No agenda entry specified. Requested by %s via Direct Message." % (message.sender_screen_name))
                        # NOT REPLYING TO SOMETHING EMPTY # self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Geen agenda id vermeld.")
                elif preParseMessage[0].upper() == "C":
                    # Forcing it in the agenda
                    logging.getLogger(__name__).debug("Request for forced adding %s by %s" % (preParseMessage, message.sender_screen_name))
                    try:
                        # Parsing it
                        agendaEntry = self.parseAgendaItem(preParseMessage, message.sender_screen_name)
                        # Reserving an ID
                        try:
                            agendaId = str(self.agenda["0"]["nextid"])
                            # This looks a bit strange, why not do it in one go?
                            # Shelve doesn't work well in that case.
                            zero = self.agenda["0"]
                            zero["nextid"] = zero["nextid"] + 1
                        except ValueError:
                            agendaId = "1"
                            zero = self.agenda["0"]
                            zero["nextid"] = 2
                        # Adding it
                        if "timestamp" not in zero:
                            zero["timestamp"] = {}
                        if agendaEntry["start"] not in zero["timestamp"]:
                            zero["timestamp"][agendaEntry["start"]] = list()
                        # Forcing the addition
                        self.__addItem(zero, message, agendaId, agendaEntry)
                    except Exception as err:
                        logging.getLogger(__name__).warn("Could not force add agenda entry %s by %s via Direct Message." % (preParseMessage, message.sender_screen_name))
                        self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Er is een fout opgetreden.")
                else:
                    # Putting it in the agenda
                    logging.getLogger(__name__).debug("Request for adding %s by %s" % (preParseMessage, message.sender_screen_name))
                    try:
                        # Parsing it
                        agendaEntry = self.parseAgendaItem(preParseMessage, message.sender_screen_name)
                        # Reserving an ID
                        try:
                            agendaId = str(self.agenda["0"]["nextid"])
                            # This looks a bit strange, why not do it in one go?
                            # Shelve doesn't work well in that case.
                            zero = self.agenda["0"]
                            zero["nextid"] = zero["nextid"] + 1
                        except ValueError:
                            agendaId = "1"
                            zero = self.agenda["0"]
                            zero["nextid"] = 2
                        # Adding it
                        if "timestamp" not in zero:
                            zero["timestamp"] = {}
                        if agendaEntry["start"] not in zero["timestamp"]:
                            zero["timestamp"][agendaEntry["start"]] = list()
                        if len(zero["timestamp"][agendaEntry["start"]]) > 0:
                            logging.getLogger(__name__).warn("There are already entries for timestamp %s: %s." % (agendaEntry["start"], ", ".join(zero["timestamp"][agendaEntry["start"]])))
                            # Notifying the poster (with ID for future reference)
                            self.__silentlyPostDirectMessage(user_id = message.sender_id, text = ("Er is al een agenda item op %s: %s." % (agendaEntry["start"], ", ".join(zero["timestamp"][agendaEntry["start"]]))))
                        else:
                            # There wasn't one yet for this timestamp, so we're safe.
                            self.__addItem(zero, message, agendaId, agendaEntry)
                    except Exception as err:
                        logging.getLogger(__name__).warn("Could not add agenda entry %s by %s via Direct Message." % (preParseMessage, message.sender_screen_name))
                        self.__silentlyPostDirectMessage(user_id = message.sender_id, text = "Er is een fout opgetreden.")
            else:
               logging.getLogger(__name__).warn("Direct message from unauthorized user: %s." % (message))

            self.api.DestroyDirectMessage(id = message.id)


    def __cleanAgenda(self, timestamp):
        """
        Cleans the agenda for a certain timestamp.

        Parameters:
            timestamp

        It will clear agenda["O"]["timestamp"][timestamp] and the agenda entries linked in it.
        """
        zero = self.agenda["0"]
        try:
            for agendaId in zero["timestamp"][timestamp]:
                try:
                    del self.agenda[agendaId]
                except:
                    logging.getLogger(__name__).warn("Failed to delete agenda entry %s." % (agendaId))

            try:
                del zero["timestamp"][timestamp]
                self.agenda["0"] = zero
            except:
                logging.getLogger(__name__).warn("Failed to delete timestamp %s." % (timestamp))
        except:
            logging.getLogger(__name__).info("Asked to delete an non existing timestamp %s." % (timestamp))


    def tweet(self, agendaId):
        """
        Sends out a tweet from an agenda entry.

        Parameters:
            agendaId: ID of the agenda entry to tweet.
        """
        agendaItem = None
        try:
            agendaItem = self.agenda[agendaId]
            self.api.PostUpdate(status = self.formatAgendaItem(agendaItem))
            logging.getLogger(__name__).info("Tweeted %s: %s." % (agendaId, agendaItem))
        except Exception as err:
            logging.getLogger(__name__).error("Error tweeting %s: %s." % (agendaId, agendaItem), exc_info = 1)
            # Stop with what we are doing and hope the next run will pick it up for us.
            raise TwitterException("Error tweeting %s: %s (%s)." % (agendaId, agendaItem, err))


    def doAgenda(self):
        """
        Tweets upcoming events from the agenda if it is time.

        Each event is tweeted 4 (or 3) times:
            The morning of the day it happens (unless it happens before 'wakinghour')
            The morning of the day before it happens.
            The morning a week before it happens.
            The morning a month (4 weeks) before it happens.
        """
        # Some initializing
        if "last execution" not in self.agenda["0"]:
            zero = self.agenda["0"]
            zero["last execution"] = "0000" + "00" + "00" + "00" + "00"
            self.agenda["0"] = zero
        if "timestamp" not in self.agenda["0"]:
            zero = self.agenda["0"]
            zero["timestamp"] = {}
            self.agenda["0"] = zero
        count = 0
        wakinghour = "0800"

        # Current datetime
        now = datetime.datetime.today()
        year = "%04d" % now.year
        month = "%02d" % now.month
        day = "%02d" % now.day
        yyyymmdd = year + month + day
        hour = "%02d" % now.hour
        minute = "%02d" % now.minute
        yyyymmddhhmm = yyyymmdd + hour + minute
        cutoff = yyyymmdd + wakinghour

        # Tomorrow
        temp = now + datetime.timedelta(1)
        tomorrow = "%04d%02d%02d" % (temp.year, temp.month, temp.day)

        # In a week
        temp = now + datetime.timedelta(7)
        inAWeek = "%04d%02d%02d" % (temp.year, temp.month, temp.day)

        # In a month (actually 4 weeks)
        temp = now + datetime.timedelta(30)
        inAMonth = "%04d%02d%02d" % (temp.year, temp.month, temp.day)

        logging.getLogger(__name__).debug("Doing agenda %s (%s, %s, %s)." % (yyyymmddhhmm, tomorrow, inAWeek, inAMonth))

        # Looping through all agenda items via timestamp
        for timestamp in self.agenda["0"]["timestamp"]:
            logging.getLogger(__name__).debug("Looking at timestamp %s." % (timestamp))
            if yyyymmdd > timestamp[:8]:
                # We already past it, so forget about it!
                logging.getLogger(__name__).info("Cleaning agenda entries for %s." % (yyyymmdd))
                self.__cleanAgenda(timestamp)
            elif yyyymmdd == timestamp[:8]:
                # Timestamp == Today
                logging.getLogger(__name__).debug("Timestamp == Today")
                if (len(timestamp) == 8) or (timestamp[8:4] > wakinghour):
                    # We only specified the date or it is during the day.
                    logging.getLogger(__name__).debug("We only spedified the date or it is during the day.")
                    if self.agenda["0"]["last execution"] < cutoff <= yyyymmddhhmm:
                        # We've not executed this yet because the cutoff wasn't reached last time.
                        # We've reached/passed the cutoff now.
                        logging.getLogger(__name__).debug("We've not executed this yet and we've reached/passed the cutoff.")
                        # So let us tweet all the stuff for today in the morning.
                        # Today meaning: unspecified hour & hours after 'wakinghour'
                        logging.getLogger(__name__).info("Agenda entries for today (after %s) on %s." % (wakinghour, timestamp))
                        for agendaId in self.agenda["0"]["timestamp"][timestamp]:
                            self.tweet(agendaId)
                            count += 1
                else:
                    # We specified date and hour and it is before wakinghour.
                    #  => We should have posted it yesterday
                    logging.getLogger(__name__).debug("We should have posted it yesterday.")
                    pass
            elif timestamp[:8] in [tomorrow, inAWeek, inAMonth]:
                # Timestamp == Tomorrow, in a week, in a month
                logging.getLogger(__name__).debug("Timestamp == Tomorrow, in a week, in a month.")
                if self.agenda["0"]["last execution"] < cutoff <= yyyymmddhhmm:
                    # We've not executed this yet because the cutoff wasn't reached last time.
                    # We've reached/passed the cutoff now.
                    logging.getLogger(__name__).debug("We've not executed this yet and we've reached/passed the cutoff.")
                    # Tweet it!
                    logging.getLogger(__name__).info("Agenda entries for tomorrow/in a week/in a month on %s." % (timestamp))
                    for agendaId in self.agenda["0"]["timestamp"][timestamp]:
                        self.tweet(agendaId)
                        count += 1
        zero = self.agenda["0"]
        zero["last execution"] = yyyymmddhhmm
        self.agenda["0"] = zero
        return count


    def step(self):
        """
        Perform one step: process the direct messages and process the agenda.
        """
        # First process the direct messages (so the agenda is up to date).
        # But even if that fails we do need to process the agenda.
        try:
            self.doDirectMessages()
            logging.getLogger(__name__).debug("Agenda after reading direct messages: %s" % (self.agenda))
        finally:
            count = self.doAgenda()
            logging.getLogger(__name__).debug("Tweeted %s messages." % (count))


    def run(self, delay=None, persist=None):
        """
        Run the steps in an indefinite loop with a certain delay.

        Parameters (optional):
            delay=   Minutes of the delay between steps
                        By default 15 minutes.
                        It will force it to be at least 2 minutes.
            persist= Pass a function to be called after each step is done.
                        Intended to be used for a persistent agenda so you can flush to disk.
        """
        # Initialize to 15 minutes if not set and make sure it is at least 2 minutes!
        if not delay:
            delay = 15
        if delay < 2:
            delay = 2
        while 1 == 1:
            try:
                self.step()
            except TwitterException as te:
                # Ignoring, we already logged it.
                pass
            except Exception as err:
                logging.getLogger(__name__).error("Step blew up:", exc_info = 1)
            if persist:
                persist()
                logging.getLogger(__name__).debug("Persisted agenda.")
            # Waiting 'delay' minutes
            logging.getLogger(__name__).debug("Now sleeping for %s minutes." % (delay))
            time.sleep(delay*60)


if __name__ == "__main__":
    logging.basicConfig(filename = os.path.expanduser("~/twitterage.log"), format = '%(asctime)s %(levelname)s %(name)s %(message)s', level = logging.DEBUG)

    # Everything info goes to the Twitter Admins
    infoMailhandler = logging.handlers.SMTPHandler("uit.telenet.be", "from@bar.org", "to@bar.org", "Twitter Log")
    infoMailhandler.addFilter(InfoFilter())
    logging.getLogger(__name__).addHandler(infoMailhandler)

    # Everything WARN (or worse) goes to the Twitter Technical Contact
    adminMailhandler = logging.handlers.SMTPHandler("uit.telenet.be", "from@bar.org", "to@bar.org", "Twitter Warn Log")
    adminMailhandler.addFilter(WarnFilter())
    logging.getLogger(__name__).addHandler(adminMailhandler)

    # First fact after the logging is in place: letting know we started.
    logging.getLogger(__name__).debug("Startup")

    # Open the agenda database
    agenda = shelve.open(os.path.expanduser("~/.twitterage"))
    logging.getLogger(__name__).debug("Currently in the agenda: %s" % (len(agenda) - 1))

    # Connecting to the Twitter api
    # Initializing the TwitterAgenda instance
    # And running it.
    try:
        import tagenda
        api = twitter.Api(consumer_key=tagenda.oauth['consumer_key'], consumer_secret=tagenda.oauth['consumer_secret'], access_token_key=tagenda.oauth["access_token_key"], access_token_secret=tagenda.oauth["access_token_secret"])
        logging.getLogger(__name__).debug(api.VerifyCredentials())
        #api = DummyTwitterAPI()
        ta = TwitterAgenda(agenda, api)
        #ta.step();agenda.sync()
        ta.run(persist = agenda.sync)
    except KeyboardInterrupt:
        # This is the normal way to stop.
        pass
    finally:
        agenda.close()
