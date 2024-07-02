#!/usr/bin/env python
# encoding: utf-8

# rospy를 ROS에서 사용하기 위해 임포트합니다.
import rospy
# move_base_msgs와 visualization_msgs로부터 메시지 타입을 임포트합니다.
from move_base_msgs.msg import MoveBaseActionResult
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PointStamped, PoseStamped

# 이동 로봇이 이동할 목표 지점의 수를 초기화합니다.
goal_count = 0
# 이동 로봇이 이전 목표 지점에 도달하지 못했을 때 다시 시도할 수 있는지 여부를 결정합니다.
try_again = True
# 이동 로봇이 목표 지점에 도달한 횟수를 초기화합니다.
goal_reached_count = 0
# 사용자가 클릭한 지점이 있는지 여부를 나타냅니다.
haved_clicked = False
# 더 많은 지점을 추가해야 하는지 여부를 결정합니다.
add_more_point = False
# MarkerArray를 사용하여 지점을 시각화합니다.
markerArray = MarkerArray()

# move_base 상태 콜백(move_base 상태 콜백)
def status_callback(msg):
    global try_again, goal_reached_count, add_more_point

    # 사용자가 클릭한 경우에만 이 콜백이 실행되어야 합니다.
    if haved_clicked:
        try:
            # 이동 로봇이 목표 지점에 도착했는지 확인합니다.
            if msg.status.status == 3 or msg.status.status == 4:  # 정상적으로 목표 지점에 도착했는지 확인합니다.
                if msg.status.status == 3:
                    goal_reached_count += 1  # 다음 지점으로 이동합니다.
                    print('****** %s번째 목표 도달 ******' % goal_reached_count)
                # 추가된 모든 지점에 대해 이동 로봇이 목표 지점에 도착하지 않았다면 다음 지점으로 이동합니다.
                if goal_reached_count < goal_count:
                    pose = PoseStamped()
                    pose.header.frame_id = map_frame
                    pose.header.stamp = rospy.Time.now()
                    pose.pose.position.x = markerArray.markers[goal_reached_count].pose.position.x
                    pose.pose.position.y = markerArray.markers[goal_reached_count].pose.position.y
                    pose.pose.orientation.w = 1
                    goal_pub.publish(pose)
                    print('****** %s번째 목표 전송 ******' % (goal_reached_count + 1))
                # 모든 지점에 도착한 경우
                elif goal_reached_count == goal_count:
                    add_more_point = True
                try_again = True
            else:  # 목표 지점에 도착하지 않았을 경우
                print('****** 목표 지점에 도달할 수 없습니다 :', msg.status.status, ' 다시 시도합니다!!!!')
                if try_again:  # 다시 시도합니다.
                    pose = PoseStamped()
                    pose.header.frame_id = map_frame
                    pose.header.stamp = rospy.Time.now()
                    pose.pose.position.x = markerArray.markers[goal_reached_count].pose.position.x
                    pose.pose.position.y = markerArray.markers[goal_reached_count].pose.position.y
                    pose.pose.orientation.w = 1
                    goal_pub.publish(pose)
                    try_again = False
                # 실패한 경우 바로 다음 지점으로 이동합니다.
                elif goal_reached_count < goal_count:
                    goal_reached_count += 1
                    pose = PoseStamped()
                    pose.header.frame_id = map_frame
                    pose.header.stamp = rospy.Time.now()
                    pose.pose.position.x = markerArray.markers[goal_reached_count].pose.position.x
                    pose.pose.position.y = markerArray.markers[goal_reached_count].pose.position.y
                    pose.pose.orientation.w = 1
                    goal_pub.publish(pose)
        except BaseException as e:
            print(e)

# 사용자가 클릭한 위치 콜백(click location callback)
def click_callback(msg):
    global add_more_point
    global goal_count, haved_clicked

    # 새로운 지점을 목록에 추가합니다.
    goal_count += 1
    print('****** %s번째 지점 추가 ******' % goal_count)

    # 클릭 지점을 숫자로 표시합니다.
    marker = Marker()
    marker.header.frame_id = map_frame
    marker.type = marker.TEXT_VIEW_FACING
    marker.action = marker.ADD
    marker.scale.x = 0.8
    marker.scale.y = 0.8
    marker.scale.z = 0.8
    marker.color.a = 1
    marker.color.r = 1
    marker.color.g = 0
    marker.color.b = 0
    marker.pose.position.x = msg.point.x
    marker.pose.position.y = msg.point.y
    marker.pose.position.z = msg.point.z
    marker.pose.orientation.w = 1
    marker.text = str(goal_count)

    # 리스트에 마커를 추가하여 표시를 유지합니다.
    markerArray.markers.append(marker)
    marker_id = 0
    for m in markerArray.markers:
        m.id = marker_id
        marker_id += 1
    mark_pub.publish(markerArray)

    # 첫 번째 지점이 추가되면 즉시 move_base로 전송합니다.
    if goal_count == 1:
        pose = PoseStamped()
        pose.header.frame_id = map_frame
        pose.header.stamp = rospy.Time.now()
        pose.pose.position.x = msg.point.x
        pose.pose.position.y = msg.point.y
        pose.pose.orientation.w = 1
        goal_pub.publish(pose)
        print('****** %s번째 목표 전송 ******' % goal_count)
    # 모든 지점이 추가되었을 때 추가 지점을 수동으로 트리거합니다.
    elif add_more_point:
        add_more_point = False
        move = MoveBaseActionResult()
        move.status.status = 4
        move.header.stamp = rospy.Time.now()
        print('****** 추가 지점 추가 ******')
        goal_status_pub.publish(move)

    haved_clicked = True


if __name__ == '__main__':
    # ROS 노드를
    # ROS 노드를 초기화합니다.
    rospy.init_node('publish_point_node')

    # 맵 프레임을 설정하고, 기본값은 'map'입니다.
    map_frame = rospy.get_param('~map_frame', 'map')
    # 사용자가 클릭한 포인트를 나타내는 ROS 토픽 이름을 설정합니다.
    clicked_point = rospy.get_param('~clicked_point', '/clocked_point')
    # 이동 로봇의 결과를 받아오는 ROS 토픽 이름을 설정합니다.
    move_base_result = rospy.get_param('~move_base_result', '/move_base/result')

    # 지점을 시각화하기 위해 MarkerArray를 발행합니다.
    mark_pub = rospy.Publisher('path_point', MarkerArray, queue_size=100)
    # 사용자가 클릭한 포인트를 구독합니다.
    click_sub = rospy.Subscriber(clicked_point, PointStamped, click_callback)

    # 이동 로봇의 목표를 전달하기 위해 PoseStamped 메시지를 발행합니다.
    goal_pub = rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=1)
    # 이동 로봇의 상태를 수신하기 위해 MoveBaseActionResult 메시지를 구독합니다.
    goal_status_sub = rospy.Subscriber(move_base_result, MoveBaseActionResult, status_callback)
    # 이동 로봇의 상태를 발행하기 위해 MoveBaseActionResult 메시지를 발행합니다.
    goal_status_pub = rospy.Publisher(move_base_result, MoveBaseActionResult, queue_size=1)

    # ROS의 스핀 함수를 호출하여 노드가 종료될 때까지 실행을 유지합니다.
    rospy.spin()
