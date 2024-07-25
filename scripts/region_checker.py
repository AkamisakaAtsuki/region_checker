#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import yaml
import time
from shapely.geometry import Point, Polygon
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Point as ROSPoint
from visualization_msgs.msg import Marker

class RegionChecker:
    def __init__(self, config_file):
        # Load settings from YAML file
        with open(config_file, 'r') as file:
            self.settings = yaml.safe_load(file)

        # Initialize ROS node
        node_name = self.settings['node']['name']
        rospy.init_node(node_name, anonymous=True)

        # Publisher setup
        topics = self.settings['topics']
        self.pub_current_region = rospy.Publisher(topics['publish']['current_region'], String, queue_size=10)  # 領域情報を発行
        self.marker_publisher = rospy.Publisher('/region_markers', Marker, queue_size=10)  # Rivzで領域情報を確認できるようにするためにMarkerを発行

        # Subscriber setup
        rospy.Subscriber(topics['subscribe']['pose'], PoseStamped, self.handle_pose)  # 領域を確認したい地図上の位置（Pose型）をサブスクライブ

        time.sleep(1)

        # Load regions from settings
        self.polygons = []
        marker_id = 0
        for region in self.settings['regions']:
            name = region['name']
            points = region['points']
            polygon = Polygon(points)
            self.polygons.append((name, polygon))
            self.publish_marker(points, marker_id, name)
            marker_id += 1

        self.regions = self.settings['regions']
        # Timer setup to publish markers every second
        rospy.Timer(rospy.Duration(1), self.publish_all_markers)

    def handle_pose(self, msg):
        point = Point(msg.pose.position.x, msg.pose.position.y)
        region_name = 'unknown'
        for name, polygon in self.polygons:
            if polygon.contains(point):
                region_name = name
                break
        self.pub_current_region.publish(region_name)

    def publish_marker(self, points, marker_id, region_name):
        # Publish polygon
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = rospy.Time.now()
        marker.ns = "regions"
        marker.id = marker_id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.scale.x = 0.1
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        for point in points:
            ros_point = ROSPoint()
            ros_point.x, ros_point.y = point
            ros_point.z = 0.0
            marker.points.append(ros_point)
        # Closing the polygon
        marker.points.append(marker.points[0])
        self.marker_publisher.publish(marker)

        # Calculate the centroid of the polygon for text placement
        centroid_x = sum(p[0] for p in points) / len(points)
        centroid_y = sum(p[1] for p in points) / len(points)

        # Publish text label
        text_marker = Marker()
        text_marker.header.frame_id = "map"
        text_marker.header.stamp = rospy.Time.now()
        text_marker.ns = "region_labels"
        text_marker.id = marker_id + 1000  # Offset to avoid conflict with polygon IDs
        text_marker.type = Marker.TEXT_VIEW_FACING
        text_marker.action = Marker.ADD
        text_marker.scale.z = 1.0  # Text height
        text_marker.color.a = 1.0
        text_marker.color.r = 0.0
        text_marker.color.g = 0.0
        text_marker.color.b = 1.0
        text_marker.pose.position.x = centroid_x
        text_marker.pose.position.y = centroid_y
        text_marker.pose.position.z = 0.0
        text_marker.text = region_name
        self.marker_publisher.publish(text_marker)
        
        rospy.loginfo("Published polygon marker: {} with points: {}".format(marker_id, points))

    def publish_all_markers(self, event):
        marker_id = 0
        for region in self.regions:
            name = region['name']
            points = region['points']
            self.publish_marker(points, marker_id, name)
            marker_id += 1

if __name__ == '__main__':
    import sys
    import os
    default_config_path = os.path.join(os.path.dirname(__file__), '../config/regions.yaml')
    filtered_argv = [arg for arg in sys.argv[1:] if not arg.startswith('__')]
    config_file = filtered_argv[0] if len(filtered_argv) > 0 else default_config_path

    checker = RegionChecker(config_file)
    rospy.spin()
