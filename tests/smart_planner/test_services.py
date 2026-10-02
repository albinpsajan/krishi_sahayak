import unittest
from apps.smart_planner.services import analyse_plot, analyse_geojson, coconut_layout, irrigation_plan, generate_plan


class SmartPlannerServiceTests(unittest.TestCase):
    def setUp(self):
        self.boundary = [[0, 0], [80, 0], [80, 55], [0, 55]]
        self.analysis = analyse_plot(self.boundary)

    def test_area_units_and_shape_are_explainable(self):
        self.assertEqual(self.analysis['area_sq_m'], 4400.0)
        self.assertAlmostEqual(self.analysis['area_acres'], 1.087, places=3)
        self.assertEqual(self.analysis['shape_type'], 'Rectangular')
        self.assertEqual(self.analysis['area_cents'], 108.7)

    def test_layout_counts_only_points_inside_marked_boundary(self):
        layout = coconut_layout(self.boundary, self.analysis['usable_area_sq_m'])
        self.assertEqual(layout['spacing_x_m'], 7.5)
        self.assertGreater(layout['estimated_tree_count'], 0)
        self.assertTrue(all(0 <= x <= 80 and 0 <= y <= 55 for x, y in layout['layout_points']))

    def test_low_budget_and_rainfed_are_cautious(self):
        layout = coconut_layout(self.boundary, self.analysis['usable_area_sq_m'])
        low = irrigation_plan(self.analysis, layout, 'well', 'low', 'low-cost')
        rain = irrigation_plan(self.analysis, layout, 'rainfed', 'high', 'water-saving')
        self.assertEqual(low['recommended_method'], 'Phased basin → drip')
        self.assertEqual(rain['recommended_method'], 'Water source verification required')
        self.assertFalse(rain['filter_required'])

    def test_generated_plan_has_visual_materials_and_disclaimer(self):
        result = generate_plan(self.analysis, {'water_source':'well','budget_level':'medium',
            'irrigation_preference':'water-saving','coconut_age':'new','soil_type':'loamy'})
        self.assertTrue(result['layout_svg'].startswith('<svg'))
        self.assertGreater(len(result['materials']), 0)
        self.assertIn('Field verification', result['disclaimer'])
        self.assertEqual(len(result['intercrops']), 3)

    def test_invalid_boundary_is_rejected(self):
        with self.assertRaises(ValueError):
            analyse_plot([[0, 0], [2, 0], [2, 2]])

    def test_geojson_area_and_normalized_ring(self):
        polygon = {"type": "Polygon", "coordinates": [[[76.6500, 10.7800], [76.6510, 10.7800], [76.6510, 10.7810], [76.6500, 10.7810], [76.6500, 10.7800]]]}
        result = analyse_geojson(polygon)
        self.assertGreater(result['area_sq_m'], 9000)
        self.assertEqual(result['coordinate_system'], 'WGS84')
        self.assertEqual(len(result['boundary_geojson']['coordinates'][0]), 5)


if __name__ == '__main__':
    unittest.main()
