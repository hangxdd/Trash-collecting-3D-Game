import viz
import vizshape
import vizact
import vizmat
import viztracker
import time
import random

viz.setMultiSample(4)
viz.fov(60)
viz.go()

# Ielādē ainu un modeļus
piazza = viz.add('piazza.osgb')
trashcan = viz.add('trashcan.obj')
trashcan.setPosition(0.45, 0.05, 2.80)
trashcan.setEuler([0, 90, 180])
trashcan.setScale(0.035, 0.035, 0.035)
arrow = viz.addChild('arrow.wrl', scale=[0.3, 0.3, 0.3])

# Aktivizē fiziku
viz.phys.enable()
piazza.collideMesh()
trashcan.collideMesh()
arrow.collideBox()
arrow.disable(viz.DYNAMICS)
arrow.disable(viz.PHYSICS)

# Sasaisti arrow ar peles izsekošanu
viewTracker = viztracker.Keyboard6DOF()
viewlink = viz.link(viewTracker, viz.MainView)
viewlink.preTrans([0, 1.5, 0])
tracker = viztracker.MouseTracker()
trackerlink = viz.link(tracker, arrow)
trackerlink.postTrans([0, 0, -5])
closest = None

# Spēlētāju punkti un loģika
player_scores = [0, 0]
current_player = 0
game_duration = 30  # sekundes
start_time = time.time()

# Punktu un taimeru displejs
score_text = viz.addText(f'Score: 0', viz.SCREEN, pos=[0.1, 0.9, 0])
score_text.fontSize(24)
time_text = viz.addText(f'Time: {game_duration}', viz.SCREEN, pos=[0.1, 0.8, 0])
time_text.fontSize(24)

# Iegūst spēlētāju vārdus
player_names = [viz.input('Enter Player 1 name:'), viz.input('Enter Player 2 name:')]

# Spēlētāja kārtas indikators
turn_indicator = viz.addText(f"Turn: {player_names[current_player]}", viz.SCREEN, pos=[0.1, 0.7, 0])
turn_indicator.fontSize(24)

# Atjaunina kārtas indikatoru
def update_turn_indicator():
    turn_indicator.message(f"Player's turn: {player_names[current_player]}")

# Atjaunina punktu displeju
def update_score():
    score_text.message(f'Score: {player_scores[current_player]}')

# Atiestata spēli nākamajam spēlētājam
def reset_game():
    global player_scores, crates
    # Noņem esošās kastes
    for crate in crates:
        crate.remove()
    crates = []
    create_crates()
    viz.MainView.setPosition(0, 1.5, 5)
    viz.MainView.setEuler(0, 0, 0)
    update_score()

# Pārbauda spēles laiku ar brīdinājumu
warning_threshold = 10

def check_time():
    global current_player, start_time
    elapsed_time = time.time() - start_time
    remaining_time = int(game_duration - elapsed_time)
    time_text.message(f"Time: {remaining_time}")
    
    if remaining_time <= warning_threshold:
        time_text.color(viz.RED)  # Maina teksta krāsu uz sarkanu brīdinājumam
    else:
        time_text.color(viz.WHITE)  # Noklusētā teksta krāsa
    
    if remaining_time <= 0:
        current_player = (current_player + 1) % 2
        if current_player == 0:
            winner = player_names[player_scores.index(max(player_scores))]
            viz.message(f"Game over! Winner is {winner} with {max(player_scores)} points!")
            viz.quit()
        else:
            viz.message(f"{player_names[current_player]}'s turn!")
            start_time = time.time()
            reset_game()
        update_turn_indicator()

# Sākotnējā kārtas indikatora atjaunināšana
update_turn_indicator()

vizact.ontimer(1, check_time)

# Fiksē spēlētāja pozīciju
fixed_position = [0, 1.5, 5]
initial_euler = [0, 0, 0]
viz.MainView.setPosition(fixed_position)
viz.MainView.setEuler(initial_euler)

def lock_position():
    viz.MainView.setPosition(fixed_position)

vizact.ontimer(0, lock_position)

# Atjaunina tuvāko objektu
def updateClosest():
    global closest
    list = viz.phys.intersectNode(arrow)
    if list:
        if piazza in list:
            list.remove(piazza)
        closestDistance = 999999
        arrowPos = arrow.getPosition()
        for obj in list:
            distance = vizmat.Distance(arrowPos, obj.getPosition())
            if distance < closestDistance:
                closest = obj
                closestDistance = distance
    else:
        closest = None

vizact.onupdate(viz.PRIORITY_DEFAULT, updateClosest)

link = None
grabbedObject = None

# Definē kastes izmērus un to punktu vērtības
crate_sizes = [
    ([0.2, 0.2, 0.2], 5),
    ([0.4, 0.4, 0.4], 10),
    ([0.6, 0.6, 0.6], 15)
]

# Funkcija, lai izveidotu kastes pozīcijās blakus atkritumu tvertnei un ne tās iekšpusē
def create_crates():
    global crates
    trashcan_pos = trashcan.getPosition()
    min_distance = 1  # Minimālais attālums no atkritumu tvertnes, lai izvairītos no iekšpusē izspaušanas

    for _ in range(3):
        while True:
            x = random.uniform(-3, 4)  # x pozīcija ap atkritumu tvertni
            y = 0.3
            z = random.uniform(2.6, 5.0)  # z pozīcija konstanta vai nedaudz mainīga ap 2.8
            distance = vizmat.Distance([x, y, z], trashcan_pos)
            if distance >= min_distance:
                break
        size, points = random.choice(crate_sizes)
        crate = viz.addChild('crate.osgb', pos=[x, y, z], scale=size)
        crate.collideBox()
        crate.points = points  # Piešķir punktu vērtību kastei
        crates.append(crate)

# Inicializē kastes sarakstu
crates = []

# Izveido sākotnējās kastes
create_crates()

# Pievieno skaņas efektus
grab_sound = viz.addAudio('grab.mp3')
dispose_sound = viz.addAudio('dispose.mp3')

def onMouseDown():
    global link, grabbedObject
    if closest and closest != trashcan:
        link = viz.grab(arrow, closest)
        grabbedObject = closest
        grab_sound.play()

def onMouseUp():
    global link, grabbedObject
    if grabbedObject:
        link.remove()
        link = None
        trashcan_pos = trashcan.getPosition()
        grabbed_pos = grabbedObject.getPosition()
        distance = vizmat.Distance(trashcan_pos, grabbed_pos)
        if distance < 1.0:
            grabbedObject.visible(False)
            grabbedObject.disable(viz.PHYSICS)
            grabbedObject.remove()
            crates.remove(grabbedObject)
            player_scores[current_player] += grabbedObject.points  # Izmanto punktu vērtību, kas piešķirta kastei
            update_score()
            dispose_sound.play()  # Atskaņo utilizācijas skaņu
            if not crates:  # Pārbauda, vai visas kastes ir utilizētas
                create_crates()  # Izveido jaunas kastes
        grabbedObject = None

vizact.onmousedown(viz.MOUSEBUTTON_LEFT, onMouseDown)
vizact.onmouseup(viz.MOUSEBUTTON_LEFT, onMouseUp)

# Nodrošina, ka galvenā loģika darbojas
if __name__ == "__main__":
    viz.go()
