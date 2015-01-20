from unittest import TestCase
from unittest import main as RunTests
from exceptions import TypeError, ValueError

# class which defines a geographic point on a map, expressed as 
# latitude (-90 to 90) and longitude (-180 to 180)
class LatLngPoint:

    # constructor, allow int or float as arguments
    def __init__(self, inLat, inLng):
        # type checking
        if type(inLat) not in [int, float]:
            raise TypeError(
                "invalid type for latitude: expected <float>|<int> got: %s" % \
                type(inLat))
        if type(inLng) not in [int, float]:
            raise TypeError(
                "invalid type for longitude: expected <float>|<int> got: %s" % \
                type(inLng))

        # bounds checking to lat/lng
        if inLat < -90.0 or inLat > 90.0:
            raise ValueError(
                "invalid latitude value: expected [-90.0, 90.0]: "\
                "got: %.2f" % inLat)
        if inLng < -180.0 or inLng > 180.0:
            raise ValueError(
                "invalid longitude value: expected [-180.0, 180.0], "\
                "got: %.2f" % inLng)

        self.latitude = inLat
        self.longitude = inLng

    # string representation
    def __str__(self):
        return "(%.2f, %.2f)" % (self.latitude, self.longitude)

    # allow addition of points
    def __add__(self, inOther):
        # type checks
        if not isinstance(inOther, LatLngPoint):
            raise TypeError(
                "invalid type for add: expected LatLngPoint got: %s" % \
                type(inOther))

        # clamp down out-of-bounds latitude values
        newLat = self.latitude + inOther.latitude
        if newLat > 90.0:
            newLat = 90
        elif newLat < -90.0:
            newLat = -90.0

        # handle wrap of longitude
        newLng = self.longitude + inOther.longitude
        if newLng > 180.0:
            newLng = -180 + (newLng-180)
        elif newLng < -180.0:
            newLng = 180 + (newLng+180)

        return LatLngPoint(newLat, newLng)
        
    # allow subtraction of points
    def __sub__(self, inOther):
        # type checks
        if not isinstance(inOther, LatLngPoint):
            raise TypeError(
                "invalid type for subtract: expected LatLngPoint got: %s" % \
                type(inOther))

        # clamp down out-of-bounds latitude values
        newLat = self.latitude - inOther.latitude
        if newLat > 90.0:
            newLat = 90
        elif newLat < -90.0:
            newLat = -90.0

        # handle wrap of longitude
        newLng = self.longitude - inOther.longitude
        if newLng > 180.0:
            newLng = -180 + (newLng-180)
        elif newLng < -180.0:
            newLng = 180 + (newLng+180)

        return LatLngPoint(newLat, newLng)
        

# class which defines the bounds of a geographic area, defined by a lower
# southwest corner and an upper northeast corner, expressed as points.
class LatLngBounds:

    # constructor requires two LatLngPoint structures
    def __init__(self, inSW, inNE):

        # type checking
        if not isinstance(inSW, LatLngPoint):
            raise TypeError(
                "invalid type for SW point: expected LatLngPoint got: %s" % \
                type(inSW))
        if not isinstance(inNE, LatLngPoint):
            raise TypeError(
                "invalid type for NE point: expected LatLngPoint got: %s" % \
                type(inNE))

        # value checking... the bounds must have a positive area
        if inSW.latitude >= inNE.latitude:
            raise ValueError(
                "invalid latitude bounds: south coord: %s must be less than "\
                "north coord: %s" % (inSW, inNE))
        if inSW.longitude == inNE.longitude:
            raise ValueError(
                "invalid longitude bounds: west coord: %s must not be equal "\
                "to east coord: %s" % (inSW, inNE))

        # check if bounds crosses date line
        if inSW.longitude > inNE.longitude:
            self.crossDateline = True
        else:
            self.crossDateline = False

        self.SW = inSW
        self.NE = inNE

    # string representation
    def __str__(self):
        return "%s - %s" % (self.SW, self.NE)

    # method to determine if the given point lies within the boundary
    # represented by this class
    # inPoint must be a LatLngPoint instance
    def Contains(self, inPoint):
        rv = False

        # type checking
        if not isinstance(inPoint, LatLngPoint):
            raise TypeError(
                "invalid type for point: expected LatLngPoint got: %s" % \
                type(inPoint))

        # if bounds crosses dateline, need to consider wrap of coordinates
        if self.crossDateline:
            rv = True
            # latitude is still straight compare
            if inPoint.latitude <= self.SW.latitude or \
               inPoint.latitude >= self.NE.latitude:
                rv = False

            if inPoint.longitude >= self.NE.longitude and \
               inPoint.longitude <= self.SW.longitude:
                rv = False

        # otherwise... straight up compare
        else:
            if inPoint.latitude > self.SW.latitude and \
               inPoint.latitude < self.NE.latitude and \
               inPoint.longitude > self.SW.longitude and \
               inPoint.longitude < self.NE.longitude:
                rv = True
               
        return rv

#------------------------------------------------------------------------------
# Test cases for the LatLngPoint class

# tests for the constructor
class TestLatLngPoint_Constructor(TestCase):

    def test_InvalidLatType(self):
        iLat = "23.0"
        iLng = 45.0
        self.assertRaisesRegexp(TypeError, "invalid type for lat.*",
            LatLngPoint, iLat, iLng)
    def test_InvalidLngType(self):
        iLat = 23.0
        iLng = "45.0"
        self.assertRaisesRegexp(TypeError, "invalid type for long.*",
            LatLngPoint, iLat, iLng)

    def test_InvalidLatValue1(self):
        iLat = 91.0
        iLng = 45.0
        self.assertRaisesRegexp(ValueError, "invalid latitude value.*",
            LatLngPoint, iLat, iLng)
    def test_InvalidLatValue2(self):
        iLat = -91.0
        iLng = 45.0
        self.assertRaisesRegexp(ValueError, "invalid latitude value.*",
            LatLngPoint, iLat, iLng)

    def test_InvalidLngValue1(self):
        iLat = 23.0
        iLng = 180.1
        self.assertRaisesRegexp(ValueError, "invalid longitude value.*",
            LatLngPoint, iLat, iLng)
    def test_InvalidLngValue1(self):
        iLat = 23.0
        iLng = -180.1
        self.assertRaisesRegexp(ValueError, "invalid longitude value.*",
            LatLngPoint, iLat, iLng)

    def test_OkLatBounds1(self):
        iLat = 90.0
        iLng = 45.0
        LatLngPoint(iLat, iLng)
    def test_OkLatBounds2(self):
        iLat = -90.0
        iLng = 45.0
        LatLngPoint(iLat, iLng)
    def test_OkLatBounds3(self):
        iLat = 0.0
        iLng = 45.0
        LatLngPoint(iLat, iLng)

    def test_OkLngBounds1(self):
        iLat = 23.0
        iLng = 180.0
        LatLngPoint(iLat, iLng)
    def test_OkLngBounds2(self):
        iLat = 23.0
        iLng = -180.0
        LatLngPoint(iLat, iLng)
    def test_OkLngBounds3(self):
        iLat = 23.0
        iLng = 0.0
        LatLngPoint(iLat, iLng)

# tests for the add method
class TestLatLngPoint_Add(TestCase):
    def test_InvalidOther(self):
        sPoint = LatLngPoint(10,10)
        self.assertRaisesRegexp(TypeError, "invalid type for add.*",
            sPoint.__add__, "(10,10)")
    def test_ClampNorth(self):
        sPoint = LatLngPoint(80,10)
        oPoint = sPoint + LatLngPoint(20,0)
        self.assertEqual(oPoint.latitude, 90)
        self.assertEqual(oPoint.longitude, 10)
    def test_ClampSouth(self):
        sPoint = LatLngPoint(-80,10)
        oPoint = sPoint + LatLngPoint(-20,0)
        self.assertEqual(oPoint.latitude, -90)
        self.assertEqual(oPoint.longitude, 10)
    def test_WrapEast(self):
        sPoint = LatLngPoint(10,170)
        oPoint = sPoint + LatLngPoint(0,20)
        self.assertEqual(oPoint.latitude, 10)
        self.assertEqual(oPoint.longitude, -170)
    def test_WrapWest(self):
        sPoint = LatLngPoint(10,-170)
        oPoint = sPoint + LatLngPoint(0,-20)
        self.assertEqual(oPoint.latitude, 10)
        self.assertEqual(oPoint.longitude, 170)

# tests for the subtract method
class TestLatLngPoint_Subtract(TestCase):
    def test_InvalidOther(self):
        sPoint = LatLngPoint(10,10)
        self.assertRaisesRegexp(TypeError, "invalid type for subtract.*",
            sPoint.__sub__, "(10,10)")
    def test_ClampNorth(self):
        sPoint = LatLngPoint(80,10)
        oPoint = sPoint - LatLngPoint(-20,0)
        self.assertEqual(oPoint.latitude, 90)
        self.assertEqual(oPoint.longitude, 10)
    def test_ClampSouth(self):
        sPoint = LatLngPoint(-80,10)
        oPoint = sPoint - LatLngPoint(20,0)
        self.assertEqual(oPoint.latitude, -90)
        self.assertEqual(oPoint.longitude, 10)
    def test_WrapEast(self):
        sPoint = LatLngPoint(10,170)
        oPoint = sPoint - LatLngPoint(0,-20)
        self.assertEqual(oPoint.latitude, 10)
        self.assertEqual(oPoint.longitude, -170)
    def test_WrapWest(self):
        sPoint = LatLngPoint(10,-170)
        oPoint = sPoint - LatLngPoint(0,20)
        self.assertEqual(oPoint.latitude, 10)
        self.assertEqual(oPoint.longitude, 170)

#------------------------------------------------------------------------------
# test cases for the LatLngBounds

# tests for the constructor
class TestLatLngBounds_Constructor(TestCase):
    def test_invalidSWType(self):
        iSW = "(23.0, 45.0)"
        iNE = LatLngPoint(24.0, 46.0)
        self.assertRaisesRegexp(TypeError, "invalid type for SW.*",
            LatLngBounds, iSW, iNE)

    def test_invalidNEType(self):
        iSW = LatLngPoint(23.0, 45.0)
        iNE = "(24.0, 46.0)"
        self.assertRaisesRegexp(TypeError, "invalid type for NE.*",
            LatLngBounds, iSW, iNE)

    def test_invalidLatBounds(self):
        iSW = LatLngPoint(10.0, 10.0)
        iNE = LatLngPoint(-10.0, 20.0)
        self.assertRaisesRegexp(ValueError, "invalid latitude bounds.*",
            LatLngBounds, iSW, iNE)

    def test_invalidLngBounds(self):
        iSW = LatLngPoint(10.0, 10.0)
        iNE = LatLngPoint(20.0, 10.0)
        self.assertRaisesRegexp(ValueError, "invalid longitude bounds.*",
            LatLngBounds, iSW, iNE)

# define a base test case for the contains method, to include:
# x Check middle point of area
# x Check at each edge (N,S,E,W)
# x Check at midpoint between center and each edge
# x Check outside of bounds at each edge
#
# Uses test lat/lng values which are all within single hemisphere
class TestLatLngBoundsContains_Base(TestCase):
    startLat = 20.0
    startLng = 20.0
    def setUp(self):

        # define the starting center point
        self.startPoint = LatLngPoint(self.startLat, self.startLng)

        # define the test bounds as +- 10 degress from starting point
        self.Bounds = LatLngBounds(
            self.startPoint-LatLngPoint(10,10),
            self.startPoint+LatLngPoint(10,10))

    def test_Center(self):
        self.assertTrue(self.Bounds.Contains(self.startPoint))
    def test_WestEdge(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint - LatLngPoint(10,0)))
    def test_EastEdge(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint + LatLngPoint(10,0)))
    def test_NorthEdge(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint + LatLngPoint(0,10)))
    def test_SouthEdge(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint - LatLngPoint(0,10)))
    def test_InWest(self):
        self.assertTrue(self.Bounds.Contains(
            self.startPoint - LatLngPoint(5,0)))
    def test_InEast(self):
        self.assertTrue(self.Bounds.Contains(
            self.startPoint + LatLngPoint(5,0)))
    def test_InNorth(self):
        self.assertTrue(self.Bounds.Contains(
            self.startPoint + LatLngPoint(0,5)))
    def test_InSouth(self):
        self.assertTrue(self.Bounds.Contains(
            self.startPoint - LatLngPoint(0,5)))
    def test_OutWest(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint - LatLngPoint(15,0)))
    def test_OutEast(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint + LatLngPoint(15,0)))
    def test_OutNorth(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint + LatLngPoint(0,15)))
    def test_OutSouth(self):
        self.assertFalse(self.Bounds.Contains(
            self.startPoint - LatLngPoint(0,15)))

# Contains test case for a bounds which crosses the meridian, because this
# derives from the _Base class, all of the same tests will be run for this
# test class
class TestLatLngBoundsContains_CrossLngMeridian(TestLatLngBoundsContains_Base):
    startLat = 20
    startLng = 0
    # runs all of the test cases defined in _Base
                                    
# Contains test case for a bounds which crosses the dateline
class TestLatLngBoundsContains_CrossLngDateline(TestLatLngBoundsContains_Base):
    startLat = 20
    startLng = 180
    # runs all of the test cases defined in _Base

# Contains test case for a bounds which crosses the equator
class TestLatLngBoundsContains_CrossLatEquator(TestLatLngBoundsContains_Base):
    startLat = 0
    startLng = 20

# Contains test case for a bounds which has an edge on the north pole
class TestLatLngBoundsContains_LatNorthPole(TestLatLngBoundsContains_Base):
    startLat = 80
    startLng = 20

    # skip the OutNorth test... as the northern bound is already the pole
    # NOTE: it would return the correct result, but only because the
    # addition clamps the value.
    def test_OutNorth(self):
        pass

# Contains test case for a bounds which has an edge on the south pole
class TestLatLngBoundsContains_LatSouthPole(TestLatLngBoundsContains_Base):
    startLat = -80
    startLng = 20

    def test_OutSouth(self):
        pass

# hook to run the unit tests
if __name__ == '__main__':
    RunTests()
