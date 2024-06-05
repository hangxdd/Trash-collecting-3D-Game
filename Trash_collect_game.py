import viz
import vizshape
import vizact
import time

# Inicializē Vizard vidi
viz.go()

# Uzstādīt fona krāsu ar vienu attēlu
sky = viz.addTexture('house_interior.jpg')
skybox = vizshape.addSphere(radius=50, slices=50, stacks=50, cullFace=False)
skybox.texture(sky)
skybox.setScale([-1, 1, 1])  # Invert the sphere so the texture is inside

# Adjust texture scale
skybox.texmat(viz.Matrix.scale(1.5, 1.5, 1.5))  # Adjust the scale values as needed

# Izveidot grīdu un uzstādīt koka tekstūru
floor = vizshape.addPlane(size=(20, 20), axis=vizshape.AXIS_Y, cullFace=False)
floor.setPosition(0, -22.5, 0)
floor.alpha(0.2)

# Spēlētāju punkti
player_scores = [0, 0]
current_player = 0

# Spēles ilgums
game_duration = 30  # sekundes
start_time = time.time()

# Piekļūt galvenajam apgaismojumam un uzstādīt tā intensitāti
head_light = viz.MainView.getHeadLight()
head_light.intensity(0.5)

# Pievienot virziena gaismu
dir_light = viz.addDirectionalLight()
dir_light.direction(0, -1, 0)
dir_light.intensity(0.8)

# Pievienot punktu tekstu fona attēlu
score_bg = viz.addTexQuad(parent=viz.SCREEN, size=(0.3, 0.1))
score_bg.setPosition(0.2, 0.9, 0)
score_bg.color(viz.BLACK)
score_bg.alpha(0.5)

# Pievienot punktu tekstu
score_text = viz.addText('Punkti: 0', parent=viz.SCREEN, pos=(0.1, 0.9, 0))
score_text.fontSize(24)
score_text.color(viz.WHITE)

# Pievienot laika tekstu fona attēlu
time_bg = viz.addTexQuad(parent=viz.SCREEN, size=(0.3, 0.1))
time_bg.setPosition(0.2, 0.8, 0)
time_bg.color(viz.BLACK)
time_bg.alpha(0.5)

# Pievienot laika atpakaļskaitīšanu
time_text = viz.addText('Laiks: 33', parent=viz.SCREEN, pos=(0.1, 0.8, 0))
time_text.fontSize(24)
time_text.color(viz.WHITE)

# Spēlētāju vārdu ievade
player_names = [viz.input('Ievadiet spēlētāja 1 vārdu:'), viz.input('Ievadiet spēlētāja 2 vārdu:')]

# Ielādēt skaņas efektus
plus_collect_sound = viz.addAudio('plus.mp3')
minus_collect_sound = viz.addAudio('minus.mp3')

# Funkcija, lai atjauninātu punktus
def update_score():
    score_text.message(f'Punkti: {player_scores[current_player]}')

# Pievienot periodisku laika skaiti
def check_time():
    global current_player, start_time
    elapsed_time = time.time() - start_time
    remaining_time = int(game_duration - elapsed_time)
    time_text.message(f'Laiks: {remaining_time}')
    if remaining_time <= 0:
        current_player = (current_player + 1) % 2
        if current_player == 0:
            winner = player_names[player_scores.index(max(player_scores))]
            viz.message(f'Spēle beigusies! Uzvarētājs ir spēlētājs {winner} ar {max(player_scores)} punktiem!')
            viz.quit()
        else:
            viz.message(f'Spēlētāja {player_names[current_player]} kārta!')
            start_time = time.time()
            reset_game()

# Funkcija, lai atiestatītu spēli nākamajam spēlētājam
def reset_game():
    global player_scores
    player_scores[1] = 0
    viz.MainView.setPosition(0, -3.2, 10)  # Move the player's initial position down
    viz.MainView.setEuler(0, 0, 0)
    update_score()

vizact.ontimer(1, check_time)

# Peles notikumu mainīgie
mouse_held = False

# Pievienot peles kustības funkcionalitāti skatīšanās virziena maiņai
def onMouseMove(e):
    if mouse_held:
        euler = viz.MainView.getEuler()
        viz.MainView.setEuler([euler[0] + e.dx * 0.1, euler[1] + e.dy * 0.1, euler[2]])

def onMouseDown(e):
    global mouse_held
    if e.button == viz.MOUSEBUTTON_LEFT:
        mouse_held = True

def onMouseUp(e):
    global mouse_held
    if e.button == viz.MOUSEBUTTON_LEFT:
        mouse_held = False

viz.callback(viz.MOUSE_MOVE_EVENT, onMouseMove)
viz.callback(viz.MOUSEDOWN_EVENT, onMouseDown)
viz.callback(viz.MOUSEUP_EVENT, onMouseUp)

# Fiksēt spēlētāja pozīciju un uzstādīt sākotnējo skatīšanās virzienu
fixed_position = [0, -20, 12.5]  # Move the player's fixed position down
initial_euler = [180, 0, 0]  # Adjust these values as needed to face the correct direction
viz.MainView.setPosition(fixed_position)
viz.MainView.setEuler(initial_euler)

def lock_position():
    viz.MainView.setPosition(fixed_position)

vizact.ontimer(0, lock_position)

# Palaist programmu
if __name__ == "__main__":
    viz.go()
