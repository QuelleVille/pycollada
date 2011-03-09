import unittest2
import collada
from lxml.etree import fromstring, tostring
import StringIO
import os
import sys

class TestMaterial(unittest2.TestCase):

    def setUp(self):
        self.dummy_collada_text = """
        <COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
        </COLLADA>
        """
        self.dummy = collada.Collada(StringIO.StringIO(self.dummy_collada_text),
                        aux_file_loader = self.image_dummy_loader)
        
        self.dummy_cimage = collada.material.CImage("yourcimage", "./whatever.tga", self.dummy)
        self.dummy.imageById["yourcimage"] = self.dummy_cimage

    def test_effect_saving(self):
        effect = collada.material.Effect("myeffect", [], "phong",
                       emission = (0.1, 0.2, 0.3),
                       ambient = (0.4, 0.5, 0.6),
                       diffuse = (0.7, 0.8, 0.9),
                       specular = (0.3, 0.2, 0.1),
                       shininess = 0.4,
                       reflective = (0.7, 0.6, 0.5),
                       reflectivity = 0.8,
                       transparent = (0.2, 0.4, 0.6),
                       transparency = 0.9)
        
        self.assertEqual(effect.id, "myeffect")
        self.assertEqual(effect.shininess, 0.4)
        self.assertEqual(effect.reflectivity, 0.8)
        self.assertEqual(effect.transparency, 0.9)
        self.assertTupleEqual(effect.emission, (0.1, 0.2, 0.3))
        self.assertTupleEqual(effect.ambient, (0.4, 0.5, 0.6))
        self.assertTupleEqual(effect.diffuse, (0.7, 0.8, 0.9))
        self.assertTupleEqual(effect.specular, (0.3, 0.2, 0.1))
        self.assertTupleEqual(effect.reflective, (0.7, 0.6, 0.5))
        self.assertTupleEqual(effect.transparent, (0.2, 0.4, 0.6))
        
        effect.id = "youreffect"
        effect.shininess = 7.0
        effect.reflectivity = 2.0
        effect.transparency = 3.0
        effect.emission = (1.1, 1.2, 1.3)
        effect.ambient = (1.4, 1.5, 1.6)
        effect.diffuse = (1.7, 1.8, 1.9)
        effect.specular = (1.3, 1.2, 1.1)
        effect.reflective = (1.7, 1.6, 1.5)
        effect.transparent = (1.2, 1.4, 1.6)
        effect.save()
        
        loaded_effect = collada.material.Effect.load(self.dummy, {},
                                    fromstring(tostring(effect.xmlnode)))
        
        self.assertEqual(effect.id, "youreffect")
        self.assertEqual(effect.shininess, 7.0)
        self.assertEqual(effect.reflectivity, 2.0)
        self.assertEqual(effect.transparency, 3.0)
        self.assertTupleEqual(effect.emission, (1.1, 1.2, 1.3))
        self.assertTupleEqual(effect.ambient, (1.4, 1.5, 1.6))
        self.assertTupleEqual(effect.diffuse, (1.7, 1.8, 1.9))
        self.assertTupleEqual(effect.specular, (1.3, 1.2, 1.1))
        self.assertTupleEqual(effect.reflective, (1.7, 1.6, 1.5))
        self.assertTupleEqual(effect.transparent, (1.2, 1.4, 1.6))
        
    def image_dummy_loader(self, fname):
        return self.image_return
        pass
    
    def test_cimage_saving(self):
        self.image_return = None
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        self.assertEqual(cimage.id, "mycimage")
        self.assertEqual(cimage.path, "./whatever.tga")
        cimage.id = "yourcimage"
        cimage.path = "./next.tga"
        cimage.save()
        loaded_cimage = collada.material.CImage.load(self.dummy, {}, fromstring(tostring(cimage.xmlnode)))
        self.assertEqual(loaded_cimage.id, "yourcimage")
        self.assertEqual(loaded_cimage.path, "./next.tga")
        self.assertEqual(loaded_cimage.data, None)
        self.assertEqual(loaded_cimage.pilimage, None)
        self.assertEqual(loaded_cimage.uintarray, None)
        self.assertEqual(loaded_cimage.floatarray, None)
        
    def test_cimage_data_loading(self):
        data_dir = os.path.join(os.path.dirname(os.path.realpath( __file__ )), "data")
        texture_file_path = os.path.join(data_dir, "duckCM.tga")
        self.failUnless(os.path.isfile(texture_file_path), "Could not find data/duckCM.tga file for testing")
        
        texdata = open(texture_file_path, 'rb').read()
        self.assertEqual(len(texdata), 786476)
        
        self.image_return = texdata
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        image_data = cimage.data
        self.assertEqual(len(image_data), 786476)
        pil_image = cimage.pilimage
        self.assertTupleEqual(pil_image.size, (512,512))
        self.assertEqual(pil_image.format, "TGA")
        
        numpy_uints = cimage.uintarray
        self.assertTupleEqual(numpy_uints.shape, (512, 512, 3))
        
        numpy_floats = cimage.floatarray
        self.assertTupleEqual(numpy_uints.shape, (512, 512, 3))

    def test_surface_saving(self):
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        surface = collada.material.Surface("mysurface", cimage)
        self.assertEqual(surface.id, "mysurface")
        self.assertEqual(surface.image.id, "mycimage")
        self.assertEqual(surface.format, "A8R8G8B8")
        surface.id = "yoursurface"
        surface.image = self.dummy_cimage
        surface.format = "OtherFormat"
        surface.save()
        loaded_surface = collada.material.Surface.load(self.dummy, {}, fromstring(tostring(surface.xmlnode)))
        self.assertEqual(loaded_surface.id, "yoursurface")
        self.assertEqual(loaded_surface.image.id, "yourcimage")
        self.assertEqual(loaded_surface.format, "OtherFormat")
        
    def test_sampler2d_saving(self):
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        surface = collada.material.Surface("mysurface", cimage)
        sampler2d = collada.material.Sampler2D("mysampler2d", surface)
        self.assertEqual(sampler2d.id, "mysampler2d")
        self.assertEqual(sampler2d.minfilter, None)
        self.assertEqual(sampler2d.magfilter, None)
        self.assertEqual(sampler2d.surface.id, "mysurface")
        sampler2d = collada.material.Sampler2D("mysampler2d", surface, "LINEAR_MIPMAP_LINEAR", "LINEAR")
        self.assertEqual(sampler2d.minfilter, "LINEAR_MIPMAP_LINEAR")
        self.assertEqual(sampler2d.magfilter, "LINEAR")
        
        other_surface = collada.material.Surface("yoursurface", cimage)
        sampler2d.id = "yoursampler2d"
        sampler2d.minfilter = "QUADRATIC_MIPMAP_WHAT"
        sampler2d.magfilter = "QUADRATIC"
        sampler2d.surface = other_surface
        sampler2d.save()
        
        loaded_sampler2d = collada.material.Sampler2D.load(self.dummy,
                                {'yoursurface':other_surface}, fromstring(tostring(sampler2d.xmlnode)))
        self.assertEqual(loaded_sampler2d.id, "yoursampler2d")
        self.assertEqual(loaded_sampler2d.surface.id, "yoursurface")
        self.assertEqual(loaded_sampler2d.minfilter, "QUADRATIC_MIPMAP_WHAT")
        self.assertEqual(loaded_sampler2d.magfilter, "QUADRATIC")
    
    def test_map_saving(self):
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        surface = collada.material.Surface("mysurface", cimage)
        sampler2d = collada.material.Sampler2D("mysampler2d", surface)
        map = collada.material.Map(sampler2d, "TEX0")
        self.assertEqual(map.sampler.id, "mysampler2d")
        self.assertEqual(map.texcoord, "TEX0")
        
        other_sampler2d = collada.material.Sampler2D("yoursampler2d", surface)
        map.sampler = other_sampler2d
        map.texcoord = "TEX1"
        map.save()
        
        loaded_map = collada.material.Map.load(self.dummy,
                            {'yoursampler2d': other_sampler2d}, fromstring(tostring(map.xmlnode)))
        self.assertEqual(map.sampler.id, "yoursampler2d")
        self.assertEqual(map.texcoord, "TEX1")
        
    def test_effect_with_params(self):
        cimage = collada.material.CImage("mycimage", "./whatever.tga", self.dummy)
        surface = collada.material.Surface("mysurface", cimage)
        sampler2d = collada.material.Sampler2D("mysampler2d", surface)
        effect = collada.material.Effect("myeffect", [surface, sampler2d], "phong",
                       emission = (0.1, 0.2, 0.3),
                       ambient = (0.4, 0.5, 0.6),
                       diffuse = (0.7, 0.8, 0.9),
                       specular = (0.3, 0.2, 0.1),
                       shininess = 0.4,
                       reflective = (0.7, 0.6, 0.5),
                       reflectivity = 0.8,
                       transparent = (0.2, 0.4, 0.6),
                       transparency = 0.9)
        
        other_cimage = collada.material.CImage("yourcimage", "./whatever.tga", self.dummy)
        other_surface = collada.material.Surface("yoursurface", other_cimage)
        other_sampler2d = collada.material.Sampler2D("yoursampler2d", other_surface)
        effect.params = [other_surface, other_sampler2d]
        effect.save()
        
        loaded_effect = collada.material.Effect.load(self.dummy, {}, fromstring(tostring(effect.xmlnode)))
        self.assertEqual(len(loaded_effect.params), 2)
        self.assertTrue(type(loaded_effect.params[0]) is collada.material.Surface)
        self.assertEqual(loaded_effect.params[0].id, "yoursurface")
        self.assertTrue(type(loaded_effect.params[1]) is collada.material.Sampler2D)
        self.assertEqual(loaded_effect.params[1].id, "yoursampler2d")

if __name__ == '__main__':
    unittest2.main()
