/*
iGoBot - a GO game playing robot
	 _ _____      ______       _   
	(_)  __ \     | ___ \     | |  
	 _| |  \/ ___ | |_/ / ___ | |_ 
	| | | __ / _ \| ___ \/ _ \| __|
	| | |_\ \ (_) | |_/ / (_) | |_ 
	|_|\____/\___/\____/ \___/ \__|
                               
Project website:
http://www.springwald.de/hi/igobot

 #########################
 # stone dispenser plate #
 #########################

 Licensed under MIT License (MIT)

 Copyright (c) 2018 Daniel Springwald | daniel@springwald.de

 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to permit
 persons to whom the Software is furnished to do so, subject to
 the following conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.

*/

function resolutionLow() = ($exportQuality==true) ? 20 : 10;
function resolutionHi() = ($exportQuality==true) ? 300 : 50;

storageHeight = 50;
plateWidth= 70;
plateHeight = 12;
storageWidth = plateWidth-10;
servoMove = 13;

module ServoAxisDisc(holeRadiusPlus) {
    discHeight = 2;
    discRadius = 10;
    //translate([0, 0, discHeight/2]) cylinder(h=discHeight, r=discRadius, $fn=resolutionLow(), center=true); 
    
    mountingHoleSpacing = 14.0/2;
    holeHeight=60;
    holeRadius = 1.9+holeRadiusPlus;
    translate([+mountingHoleSpacing,0, 2+holeHeight/2]) cylinder(h=holeHeight, r=holeRadius, $fn=resolutionLow(), center=true); 
    translate([-mountingHoleSpacing,0, 2+holeHeight/2]) cylinder(h=holeHeight, r=holeRadius, $fn=resolutionLow(), center=true); 
    translate([0,+mountingHoleSpacing, 2+holeHeight/2]) cylinder(h=holeHeight, r=holeRadius, $fn=resolutionLow(), center=true); 
    translate([0,-mountingHoleSpacing, 2+holeHeight/2]) cylinder(h=holeHeight, r=holeRadius, $fn=resolutionLow(), center=true); 
    
    // Screw hole middle
    translate([0,0, 2+holeHeight/2])  cylinder(h=holeHeight, r=3+holeRadiusPlus, $fn=resolutionLow(), center=true); 
}

module GoStone() {
    height = 10;
    diameter = 23;
    color([1,0,0]) {
        cylinder(h=height, r=diameter/2, $fn=resolutionHi(), center=true); 
        //cylinder(h=height*10, r=diameter/3, $fn=resolutionHi(), center=true); 
    }
}

module MakerBeamHoles() {
    height  = 40;
    radius = 3.3;
    for(y = [0 : 10: height]) {
        translate([0,30,y+5]) {
            rotate( [0,90,90]) 
            {
                cylinder(h=30, r=radius/2, $fn=resolutionLow(), center=true); // base body corner
            }
        }
    }
}

module StorageShape(height, radius, widthAddScale, margin) {
    linear_extrude(height, center = true, convexity = 100, scale=widthAddScale + margin/radius) 
        translate([0, -radius-margin, 0])
            circle(r=radius, $fn=resolutionHi());
}

module Storage3() {
    widthAddScale = 1.7;
    margin = 3;
    difference() 
    {
        color([0.7,0.7,1]) 
        {
         translate([0, storageWidth/2 , storageHeight / 2]) 
            difference() {
                StorageShape(storageHeight, storageWidth/2, widthAddScale, 0);
                radiusMinusElement = (storageWidth-margin*2)/2;
                translate([0, margin/2 ,0]) 
                    StorageShape(storageHeight+2,radiusMinusElement , widthAddScale , margin);
            }
         translate([0,storageWidth/2,storageHeight/2]) cube([10,2,storageHeight], center=true);
        }
     MakerBeamHoles();
    }
}

module Plate(rotation) {
    
    // The servo holder
    difference() 
    {
        translate([0,servoMove,-plateHeight/2]) 
        {
            cylinder(h=plateHeight, r=20, $fn=resolutionHi(), center=true); 
        }
        union() {
            rotate([0,180,0]) translate([0,servoMove,-10]) ServoAxisDisc(holeRadiusPlus=0);
            rotate([0,0,0]) translate([0,servoMove,-65]) ServoAxisDisc(holeRadiusPlus=3);
        }
    }

    // The plate
    difference() 
    {
        union()
        {
            for (i = [-45:45]) {
                rotate([0,0,i]) {
                    translate([0,-plateWidth/2,-plateHeight/2]) cylinder(h=plateHeight, r=plateWidth/2, $fn=resolutionHi(), center=true); 
                }
            }
        }
        union() {
           rotate([0,0,45]) {
            translate([0,-plateWidth/2,-4.9])  GoStone();
           }
        }
    }

    
}



//$exportQuality = false;
color([0,1,0]) cylinder(h=200, r=1, $fn=resolutionLow(), center=true); 

translate([0,0,1]) Storage3(); 


translate([0,plateWidth/2,0]) {
    rotate([0,0,0]) {
        Plate();
    }
}



