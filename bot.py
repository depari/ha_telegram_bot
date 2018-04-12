# -*- coding: utf-8 -*-

import configparser
import logging
import logging.handlers

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
logger = logging.getLogger('urung_bot')
cm = None


def errorHandler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


class UrungBotCommands:
    def __init__(self):
        pass

    def commandStart(bot, update):
        logger.info('ENTER')
        update.message.reply_text('Hi!')

    def commandHelp(bot, update):
        logger.info('ENTER')
        reply_text = 'Help!'
        logger.info('Reply Text : %s' % reply_text)
        update.message.reply_text(reply_text)

    def commandReload(bot, update):
        pass

    def commandTakePicture(bot, update, args):
        logger.info('commandTakePicture')
        update.message.reply_text('take Picture!')

        RTSP_URL = UrungBotConfig['RTSP']
        try:
            for url in RTSP_URL:
                logger.info('trying url : ' + url)
                t = 0
                out = 'tele_do.jpg'
                replyf = 'jpg'
                cmdline = '/usr/bin/ffmpeg -y -rtsp_transport tcp -i ' + url + ' -vframes 1 ' + out

                if args:
                    t = int(args[0])
                    if t >= 1 and t <= 10:
                        out = 'tele_do.gif'
                        replyf = 'gif'
                        cmdline = '/usr/bin/ffmpeg -y -rtsp_transport tcp -i ' + url + ' -t ' + str(
                            t) + ' -vf fps=1,scale=iw/4:-1 ' + out
                    else:
                        reply_text = '지원 가능 범위 1 ~ 10'
                        logger.info('Reply Text : %s' % reply_text)
                        update.message.reply_text(text=reply_text, parse_mode=ParseMode.MARKDOWN)

                import subprocess
                cmdline.split(' ')
                logger.info('cmdline : ' + cmdline)
                p = subprocess.Popen(cmdline, shell=True)
                p.wait(10 + t)
                if replyf == 'jpg':
                    update.message.reply_photo(photo=open(out, 'rb'))
                else:
                    update.message.reply_document(document=open(out, 'rb'))
        except Exception as e:
            logger.error(e)
            reply_text = '에러가 발생하였습니다.'
            logger.info('Reply Text : %s' % reply_text)
            update.message.reply_text(text=reply_text, parse_mode=ParseMode.MARKDOWN)
            print(e)


Commands = [{'command': 'start', 'alt_command': '시작', 'pass_args': False, 'description': 'start the bot',
             'handler': UrungBotCommands.commandStart},
            {'command': 'help', 'alt_command': '도움', 'pass_args': False, 'description': 'display help',
             'handler': UrungBotCommands.commandHelp},
            {'command': 'reload', 'alt_command': '리로드', 'pass_args': False, 'description': 'reload sub module',
             'handler': UrungBotCommands.commandReload},
            {'command': 'picture', 'alt_command': '사진', 'pass_args': True, 'description': 'take picture',
             'handler': UrungBotCommands.commandTakePicture}
            ]


def messageHandler(bot, update):
    logger.info('Input Text : %s' % update.message.text)
    SplitCommand = update.message.text.split()

    TestCommand = SplitCommand[0][:-1]

    if SplitCommand[0][-1] == '?':  # command
        logger.info('Command Mode')
        Matched = False
        for command in Commands:
            if TestCommand == command['alt_command']:
                logger.info('Alt Command match : %s' % command['alt_command'])
                Matched = True
                if command['pass_args'] == True:
                    command['handler'](bot, update, SplitCommand[1:])
                else:
                    command['handler'](bot, update)

        if Matched == False:
            logger.info('No match : %s' % TestCommand)
            pass
            # CoffeeGangBotCommands.commandImageSearch(bot, update, [TestCommand])

        # update.message.reply_text(update.message.text)


class UrungBot:
    ConfigFile = 'Ha.ini'
    LogFile = 'HABot.log'
    Config = {}

    def __init__(self):
        pass

    def Init(self):
        try:
            # setup logger
            logger.setLevel(logging.DEBUG)
            Formatter = logging.Formatter(
                '[%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s] %(asctime)s : %(message)s')

            StreamHandler = logging.StreamHandler()
            StreamHandler.setFormatter(Formatter)
            FileHandler = logging.FileHandler(self.LogFile)
            StreamHandler.setFormatter(Formatter)

            logger.addHandler(StreamHandler)
            logger.addHandler(FileHandler)
            logger.info('HABot Start')

            self.ReadConfig()

        except:
            logger.error('initialize failed.')
            raise
        else:
            pass

    def ReadConfig(self):
        config = configparser.ConfigParser()
        config.read(self.ConfigFile)
        try:
            if not config.has_section('Global'):
                config.add_section('Global')
            if not config.has_section('Log'):
                config.add_section('Log')
            if not config.has_section('HA'):
                config.add_section('HA')
            if not config.has_section('Camera'):
                config.add_section('Camera')

            token = config.get('Global', 'TOKEN', fallback='specify your token here')
            loglevel = config.get('Log', 'LEVEL', fallback='INFO')
            rtsp_1 = config.get('Camera', 'RTSP1', fallback='')

            config.set('Global', 'TOKEN', token)
            config.set('Log', 'LEVEL', loglevel)
            config.set('Camera', 'RTSP1', rtsp_1)

        except Exception as e:
            logger.error(e)
            return None
        else:
            logger.info('Using Telegram HTTP API Token: %s' % (token))
            self.Config['TOKEN'] = token
            self.Config.setdefault('RTSP', []).append(rtsp_1)
            # self.Config['RTSP'].remove('')

            logger.info('Log Level: %s' % (loglevel))
            if str.upper(loglevel) == 'ERROR':
                logger.setLevel(logging.ERROR)
            elif str.upper(loglevel) == 'WARNING':
                logger.setLevel(logging.WARNING)
            elif str.upper(loglevel) == 'INFO':
                logger.setLevel(logging.INFO)
            elif str.upper(loglevel) == 'DEBUG':
                logger.setLevel(logging.DEBUG)
            else:
                logger.error('Log Level %s is not proper level. use ERROR level instead.' % (loglevel))
                logger.setLevel(logging.ERROR)
            self.WriteConfig(config)
            global UrungBotConfig
            UrungBotConfig = self.Config
    def WriteConfig(self, config):
        logger.error('Writing config file as : %s' % (self.ConfigFile))

        with open(self.ConfigFile, 'w') as configfile:
            config.write(configfile)


    def Main(self):
        updater = Updater(self.Config['TOKEN'])

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        for command in Commands:
            logger.info('Registering command : %s' % (command['command']))
            dp.add_handler(CommandHandler(command['command'], command['handler'], pass_args=command['pass_args']))

        dp.add_handler(MessageHandler(Filters.text, messageHandler))

        # log all errors
        dp.add_error_handler(errorHandler)

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    cgb = UrungBot()
    cgb.Init()
    cgb.Main()
