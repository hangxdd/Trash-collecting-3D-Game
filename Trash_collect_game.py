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

# Load scene and models
piazza = viz.add('piazza.osgb')
trashcan = viz.add('trashcan.obj')
trashcan.setPosition(0.45, 0.05, 2.80)
trashcan.setEuler([0, 90, 180])
trashcan.setScale(0.035, 0.035, 0.035)
arrow = viz.addChild('arrow.wrl', scale=[0.3, 0.3, 0.3])

# Enable physics
viz.phys.enable()
piazza.collideMesh()
trashcan.collideMesh()
arrow.collideBox()
arrow.disable(viz.DYNAMICS)
arrow.disable(viz.PHYSICS)

# Link arrow to mousetracker
viewTracker = viztracker.Keyboard6DOF()
viewlink = viz.link(viewTracker, viz.MainView)
viewlink.preTrans([0, 1.5, 0])
tracker = viztracker.MouseTracker()
trackerlink = viz.link(tracker, arrow)
trackerlink.postTrans([0, 0, -5])
closest = None

# Player scores and logic
player_scores = [0, 0]
current_player = 0
game_duration = 30  # seconds
start_time = time.time()

# Score and timer display
score_text = viz.addText(f'Score: 0', viz.SCREEN, pos=[0.1, 0.9, 0])
score_text.fontSize(24)
time_text = viz.addText(f'Time: {game_duration}', viz.SCREEN, pos=[0.1, 0.8, 0])
time_text.fontSize(24)

# Get player names
player_names = [viz.input('Enter Player 1 name:'), viz.input('Enter Player 2 name:')]

# Player turn indicator
turn_indicator = viz.addText(f"Turn: {player_names[current_player]}", viz.SCREEN, pos=[0.1, 0.7, 0])
turn_indicator.fontSize(24)

# Update the turn indicator
def update_turn_indicator():
    turn_indicator.message(f"Player's turn: {player_names[current_player]}")

# Update score display
def update_score():
    score_text.message(f'Score: {player_scores[current_player]}')

# Reset game for next player
def reset_game():
    global player_scores, crates
    # Remove existing crates
    for crate in crates:
        crate.remove()
    crates = []
    create_crates()
    viz.MainView.setPosition(0, 1.5, 5)
    viz.MainView.setEuler(0, 0, 0)
    update_score()

# Check game time with warning
warning_threshold = 10

def check_time():
    global current_player, start_time
    elapsed_time = time.time() - start_time
    remaining_time = int(game_duration - elapsed_time)
    time_text.message(f"Time: {remaining_time}")
    
    if remaining_time <= warning_threshold:
        time_text.color(viz.RED)  # Change text color to red for warning
    else:
        time_text.color(viz.WHITE)  # Default text color
    
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

# Initial update of the turn indicator
update_turn_indicator()

vizact.ontimer(1, check_time)

# Fix player position
fixed_position = [0, 1.5, 5]
initial_euler = [0, 0, 0]
viz.MainView.setPosition(fixed_position)
viz.MainView.setEuler(initial_euler)

def lock_position():
    viz.MainView.setPosition(fixed_position)

vizact.ontimer(0, lock_position)

# Closest object update
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

# Define crate sizes and their point values
crate_sizes = [
    ([0.2, 0.2, 0.2], 5),
    ([0.4, 0.4, 0.4], 10),
    ([0.6, 0.6, 0.6], 15)
]

# Function to create crates with positions to the sides of the trashcan and not inside it
def create_crates():
    global crates
    trashcan_pos = trashcan.getPosition()
    min_distance = 0.5  # Minimum distance from the trashcan to avoid spawning inside it

    for _ in range(3):
        while True:
            x = random.uniform(-1.5, 2.4)  # x position around the trashcan
            y = 0.3
            z = random.uniform(2.6, 3.0)  # z position constant or slightly varying around 2.8
            distance = vizmat.Distance([x, y, z], trashcan_pos)
            if distance >= min_distance:
                break
        size, points = random.choice(crate_sizes)
        crate = viz.addChild('crate.osgb', pos=[x, y, z], scale=size)
        crate.collideBox()
        crate.points = points  # Assign point value to the crate
        crates.append(crate)

# Initialize crates list
crates = []

# Create initial crates
create_crates()

# Add sound effects
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
            player_scores[current_player] += grabbedObject.points  # Use the point value assigned to the crate
            update_score()
            dispose_sound.play()  # Play dispose sound
            if not crates:  # Check if all crates are disposed
                create_crates()  # Create new crates
        grabbedObject = None

vizact.onmousedown(viz.MOUSEBUTTON_LEFT, onMouseDown)
vizact.onmouseup(viz.MOUSEBUTTON_LEFT, onMouseUp)

# Ensure main logic runs
if __name__ == "__main__":
    viz.go()
