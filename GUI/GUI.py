import sys
import pygame
pygame.init()

size = width, height = 480, 320
background_color = 25, 179, 230
black = 0,0,0

screen = pygame.display.set_mode(size)

#load images
LUP = pygame.image.load("arrowUp.png")
LDOWN = pygame.image.load("arrowDown.png")
UUP = pygame.image.load("arrowUp.png")
UDOWN = pygame.image.load("arrowDown.png")
SettingsMenu = pygame.image.load("gear.png")
SettingsHeader = pygame.image.load("SettingsHeader.png")
Back = pygame.image.load("back.png")

CurrentTempFont = pygame.font.SysFont("monospace", 60)
rangefont = pygame.font.SysFont("monospace", 30)
settingsFont = pygame.font.SysFont("monospace", 20)

# render text
CurrentTemp = CurrentTempFont.render("23C", 1, (255,255,0))

LowerTemp = 20
UpperTemp = 25

#position of the arrows
LUPrect = pygame.Rect(0.1*width,0.1*height,64,64)
LDOWNrect = pygame.Rect(0.1*width,0.7*height,64,64)
RUPrect = pygame.Rect(0.8*width,0.1*height,64,64)
RDOWNrect = pygame.Rect(0.8*width,0.7*height,64,64)

SettingsMenurec = pygame.Rect(0.45*width,0.7*height,64,100)
SettingsHeaderrec = pygame.Rect(0.32*width,0,1,1)
Backrec = pygame.Rect(0.35*width,0.8*height,150,35) 

#MAIN LOOP
while 1:
    curPos = (0,0)
    #CHECK FOR EVENT
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            curPos = pygame.mouse.get_pos()
            print (curPos)
            if (LUPrect.collidepoint(curPos)):
                #print ("YOU HIT Left UP ARROW")
                LowerTemp +=1
            if (LDOWNrect.collidepoint(curPos)):
                #print ("YOU HIT Left DOWN ARROW")
                LowerTemp -=1
            if (RUPrect.collidepoint(curPos)):
                #print ("YOU HIT Right UP ARROW")
                UpperTemp +=1
            if (RDOWNrect.collidepoint(curPos)):
                #print ("YOU HIT Right Down ARROW")
                UpperTemp -=1
            if (SettingsMenurec.collidepoint(curPos)):
                #print ("YOU HIT Settings")
                while 1:
                    curPos = (0,0)
                    back = False
                    # print settings menu
                    screen.fill(background_color)
                    screen.blit(SettingsHeader, SettingsHeaderrec)
                    screen.blit(Back, Backrec)
                    
                    #display settings menu options
                    screen.blit(settingsFont.render("Timezone", 1, (0,0,0)), (0.1*width, 0.2*height))
                    screen.blit(settingsFont.render("City", 1, (0,0,0)), (0.1*width, 0.2*height + 20))                    
                    screen.blit(settingsFont.render("Country", 1, (0,0,0)), (0.1*width, 0.2*height + 40))
                    screen.blit(settingsFont.render("Temperature Unit", 1, (0,0,0)), (0.1*width, 0.2*height + 60))
                    screen.blit(settingsFont.render("House Type", 1, (0,0,0)), (0.1*width, 0.2*height + 80))
                    screen.blit(settingsFont.render("House Size", 1, (0,0,0)), (0.1*width, 0.2*height + 100))
                    screen.blit(settingsFont.render("Temp. Low Range", 1, (0,0,0)), (0.1*width, 0.2*height + 120))
                    screen.blit(settingsFont.render("Temp. High Range", 1, (0,0,0)), (0.1*width, 0.2*height + 140))
                    
                    # Assign variables
                    Timezone = "EST"
                    City = "Toronto"
                    Country = "Canada"
                    TemperatureUnit = "Celcius"
                    HouseType = "apartment"
                    HouseSize = "700"
                    
                    #display variables
                    screen.blit(settingsFont.render(Timezone, 1, (0,0,0)), (0.6*width, 0.2*height))
                    screen.blit(settingsFont.render(City, 1, (0,0,0)), (0.6*width, 0.2*height + 20))                    
                    screen.blit(settingsFont.render(Country, 1, (0,0,0)), (0.6*width, 0.2*height + 40))
                    screen.blit(settingsFont.render(TemperatureUnit, 1, (0,0,0)), (0.6*width, 0.2*height + 60))
                    screen.blit(settingsFont.render(HouseType, 1, (0,0,0)), (0.6*width, 0.2*height + 80))
                    screen.blit(settingsFont.render(HouseSize, 1, (0,0,0)), (0.6*width, 0.2*height + 100))
                    screen.blit(settingsFont.render(str(LowerTemp), 1, (0,0,0)), (0.6*width, 0.2*height + 120))
                    screen.blit(settingsFont.render(str(UpperTemp), 1, (0,0,0)), (0.6*width, 0.2*height + 140))
                    
                    pygame.display.flip()
                    #CHECK FOR EVENT
                    for event in pygame.event.get():
                         if event.type == pygame.QUIT: sys.exit()
                         if event.type == pygame.MOUSEBUTTONUP:
                             curPos = pygame.mouse.get_pos()
                             print (curPos)
                             if (Backrec.collidepoint(curPos)):
                                 curPos = pygame.mouse.get_pos()
                                 print (curPos)
                                 #print ("YOU HIT BACK")
                                 back = True
                                 break
                    if (back == True):
                        break
                

    #RE RENDERS TEXT
    lowerRange = rangefont.render(str(LowerTemp) + "C", 1, (255,255,0))
    upperRange = rangefont.render(str(UpperTemp) + "C", 1, (255,255,0))

    #DRAW IMAGES
    screen.fill(background_color)
    screen.blit(LUP, LUPrect)
    screen.blit(LDOWN, LDOWNrect)
    screen.blit(UUP, RUPrect)
    screen.blit(UDOWN, RDOWNrect)
    screen.blit(SettingsMenu, SettingsMenurec)
    
    #DRAW Texts
    screen.blit(CurrentTemp, (0.4*width, 0.4*height))
    screen.blit(lowerRange, (0.1*width, 0.4*height))
    screen.blit(upperRange, (0.8*width, 0.4*height))
    pygame.display.flip()
