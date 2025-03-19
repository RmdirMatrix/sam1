import math, time

OPONENT_GOAL_Y = 1.5


def define_variables(robot):
    robot.xr = 0 
    robot.yr = 0
    robot.heading = 0
    robot.xb = 0
    robot.yb = 0
    robot.ball_angle = 0
    robot.ball_distance = 0
    robot.is_ball = False
    robot.yt = 0
    robot.xt = 0
    robot.arrived_to_target = False
    robot.robotposes = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    robot.role = 'Forward'
    robot.start_time = time.time()
    robot.last_xb = 0
    robot.last_yb = 0
    robot.last_xr = 0
    robot.last_yr = 0
    robot.ball_stop_time = 0
    robot.robot_stop_time = 0
    robot.penalty_area_time = 0
    robot.goalkeeper_running = False
    robot.is_defence_robot = False
    robot.goalkeeper_x = 0
############################ محاسبات
def dist(x1, y1, x2, y2):
    return math.sqrt((y1 - y2)**2 + (x1 - x2)**2)
def clamp(a, min_, max_):
    if a < min_: return min_
    if a > max_: return max_
    return a
############################ حرکتی
def motor(robot, vl, vr):
    if vr > 10: vr = 10
    if vr <-10: vr =-10
    if vl > 10: vl = 10
    if vl <-10: vl =-10
    robot.right_motor.setVelocity(vr)
    robot.left_motor.setVelocity(vl)
def move(robot, x, y):
    angle = math.degrees(math.atan2(robot.xr - x, y - robot.yr))
    dest_angle = robot.heading - angle
    if dest_angle > 180: dest_angle -= 360
    if dest_angle <-180: dest_angle += 360

    if dist(robot.xr, robot.yr, x, y) < 0.02 and not robot.is_ball:
        stop(robot)
    elif dest_angle > -90 and dest_angle < 90:
        motor(robot, 10 - dest_angle*0.4, 10 + dest_angle*0.4)
    else:
        if dest_angle >= 0: dest_angle -= 180
        else:               dest_angle += 180
        motor(robot, -10 - dest_angle*0.4, -10 + dest_angle*0.4)
def moveAndLook(robot, x, y, x1, y1):
    angle = math.degrees(math.atan2(robot.xr - x, y - robot.yr))
    dest_angle = robot.heading - angle
    if dest_angle > 180: dest_angle -= 360
    if dest_angle <-180: dest_angle += 360

    if dist(robot.xr, robot.yr, x, y) < 0.02:
        angle = math.degrees(math.atan2(robot.xr - x1, y1 - robot.yr))
        dest_angle = robot.heading - angle
        if dest_angle > 180: dest_angle -= 360
        if dest_angle <-180: dest_angle += 360
        motor(robot, -dest_angle*0.4, dest_angle*0.4)
    elif dest_angle > -90 and dest_angle < 90:
        motor(robot, 10 - dest_angle*0.4, 10 + dest_angle*0.4)
    else:
        if dest_angle >= 0: dest_angle -= 180
        else:               dest_angle += 180
        motor(robot, -10 - dest_angle*0.4, -10 + dest_angle*0.4)   
def stop(robot):
    robot.left_motor.setVelocity(0)
    robot.right_motor.setVelocity(0)

############################ خواندن داده ها
def readData(robot):
    pos = robot.get_gps_coordinates()
    robot.heading = math.degrees(robot.get_compass_heading())
    robot.xr = pos[0]
    robot.yr = pos[1]
    if robot.robot.getName()[0] == 'B':
        robot.xr *= -1
        robot.yr *= -1
    if robot.is_new_ball_data():
        robot.is_ball = True
        ball_data = robot.get_new_ball_data()
        robot.ball_angle = math.degrees(math.atan2(ball_data['direction'][1], ball_data['direction'][0]))
        robot.ball_distance = abs(0.01666666/(abs(ball_data['direction'][2])/math.sqrt(1 - ball_data['direction'][2]**2)))
        robot.xb = -math.sin(math.radians(robot.ball_angle + robot.heading)) * robot.ball_distance + robot.xr
        robot.yb =  math.cos(math.radians(robot.ball_angle + robot.heading)) * robot.ball_distance + robot.yr
    else:
        robot.is_ball = False
    ###################################### Find Behind Ball Spot
    if robot.xb != 0 and robot.yb != OPONENT_GOAL_Y:
            m = (robot.yb - OPONENT_GOAL_Y) / robot.xb
            b = OPONENT_GOAL_Y
            robot.yt = robot.yb - 0.1
            robot.xt = (robot.yb - 0.1 - b)/m
    ###################################### Ersal Data be team
    robot.send_data_to_team({
        'is_ball': robot.is_ball,
        'xb': robot.xb,
        'yb': robot.yb,
        'xr': robot.xr,
        'yr': robot.yr,
        'id': int(robot.robot.getName()[1]) - 1
    })
    ###################################### Daryaft Data az team
    while robot.is_new_team_data():
        team_data = robot.get_new_team_data()['robot_id']
        if not robot.is_ball and team_data['is_ball']:
            robot.xb = team_data['xb']
            robot.yb = team_data['yb']
            robot.is_ball = True
        robot.robotposes[team_data['id']] = [
            team_data['xr'], 
            team_data['yr'], 
            dist(team_data['xr'], team_data['yr'], robot.xb, robot.yb)
        ]
    robot.robotposes[int(robot.robot.getName()[1]) - 1] = [robot.xr, robot.yr, robot.ball_distance]
    ###################################### Peyda kardane doortarin robot
    doortarin = robot.robotposes[0][2]
    doortarinID = 1
    nazdiktarin = robot.robotposes[0][2]
    nazdiktarinID = 1
    for i in range(3):
        if robot.robotposes[i][2] > doortarin:
            doortarin = robot.robotposes[i][2]
            doortarinID = i + 1
        if robot.robotposes[i][2] < nazdiktarin:
            nazdiktarin = robot.robotposes[i][2]
            nazdiktarinID = i + 1
    ###################################### Moshakhas kardane naghshe robot
    if int(robot.robot.getName()[1]) == doortarinID:
        robot.role = 'GoalKeeper'
    else:
        robot.role = 'Forward'
        if int(robot.robot.getName()[1]) != nazdiktarinID:
            robot.is_defence_robot = True
        else:
            robot.is_defence_robot = False
    ###################################### Tashkhis Harekate toop va robot va penalty area time
    step = 1
    threshold = 0.1
    if time.time() - robot.start_time > step:
        if(robot.xb - robot.last_yb != 0) and robot.yb < robot.last_yb:
            m = (robot.yb - robot.last_yb) / (robot.xb - robot.last_yb)
            b = robot.yb - robot.xb * m
            
            if m != 0: robot.goalkeeper_x = (-0.55 - b)/m
            else:      robot.goalkeeper_x = robot.xb
        else: robot.goalkeeper_x = robot.xb

        if dist(robot.last_xb, robot.last_yb, robot.xb, robot.yb) < threshold:
            robot.ball_stop_time += step
        else:
            robot.ball_stop_time = 0
        if dist(robot.last_xr, robot.last_yr, robot.xr, robot.yr) < threshold:
            robot.robot_stop_time += step
        else:
            robot.robot_stop_time = 0
        if robot.xr > -0.35 and robot.xr < 0.35 and robot.yr < -0.59:
            robot.penalty_area_time += step
        else:
            robot.penalty_area_time = 0
        robot.last_xb = robot.xb
        robot.last_yb = robot.yb
        robot.last_xr = robot.xr
        robot.last_yr = robot.yr
        robot.start_time = time.time()
def get_nearest_neutral_spot(robot):
    ALL_NEUTRAL_SPOTS = [
        [ 0   ,  0   ,  0    , -0.15],
        [-0.3 , -0.3 , -0.38 , -0.42],
        [ 0   , -0.2 ,  0    , -0.35],
        [ 0.3 , -0.3 ,  0.38 , -0.42],
        [ 0.3 ,  0.3 ,  0.36 ,  0.15],
        [ 0   ,  0.2 ,  0    ,  0.5 ],
        [-0.3 ,  0.3 , -0.36 ,  0.15],
    ]
    NEUTRAL_SPOTS = []
    for i in range(len(ALL_NEUTRAL_SPOTS)):
        for j in range(3):
            if dist(robot.robotposes[j][0], robot.robotposes[j][1], ALL_NEUTRAL_SPOTS[i][0], ALL_NEUTRAL_SPOTS[i][1]) > 0.08:
                NEUTRAL_SPOTS.append(ALL_NEUTRAL_SPOTS[i])
    min_dist = dist(robot.xb, robot.yb, NEUTRAL_SPOTS[0][0], NEUTRAL_SPOTS[0][1])
    min_index = 0
    for i in range(len(NEUTRAL_SPOTS)):
        if dist(robot.xb, robot.yb, NEUTRAL_SPOTS[i][0], NEUTRAL_SPOTS[i][1]) < min_dist:
            min_dist = dist(robot.xb, robot.yb, NEUTRAL_SPOTS[i][0], NEUTRAL_SPOTS[i][1])
            min_index = i
    return NEUTRAL_SPOTS[min_index]
def PenaltyAreaTimeout(robot):
    robot.goalkeeper_running = True
    move(robot, robot.xb, 0)
    if(robot.yr > -0.2):
        robot.goalkeeper_running = False

############################ AI
def Formation(robot):
    if robot.robot.getName()[1] == '1':
        moveAndLook(robot, 0, -0.6, 0, 0.75)
    if robot.robot.getName()[1] == '2':
        moveAndLook(robot, -0.3, -0.2, 0, 0.75)
    if robot.robot.getName()[1] == '3':
        moveAndLook(robot, 0.3, -0.2, 0, 0.75)
    