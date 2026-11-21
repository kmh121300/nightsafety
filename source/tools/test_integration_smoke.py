import pathlib
import tempfile
import unittest
from unittest.mock import patch

import integration_smoke


class EvidencePreservationTests(unittest.TestCase):
    def test_floating_input_is_uncovered_before_clicking_it(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        target = {'resource-id': 'destination_input', 'bounds': '[100,300][800,400]'}
        map_node = {'resource-id': 'map_container', 'bounds': '[0,0][1000,1200]'}
        sheet = {'resource-id': 'controls_scroll', 'bounds': '[0,200][1000,1200]'}
        smoke.nodes = [map_node, sheet, target]
        def collapse(*args):
            sheet['bounds'] = '[0,900][1000,1200]'
        with patch.object(smoke, 'dump'), patch.object(smoke, 'shell', side_effect=collapse) as shell:
            self.assertIs(smoke.visible('destination_input'), target)
        shell.assert_called_once()

    def test_small_panel_search_passes_ten_half_screen_steps_without_repeating_the_top(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        scroll = {'class': 'android.widget.ScrollView', 'bounds': '[30,100][1030,300]'}
        target = {'resource-id': 'deep-control', 'bounds': '[80,200][900,250]'}
        position = 0
        smoke.nodes = [scroll, {'text': '0'}]
        def swipe(*args):
            nonlocal position
            position = min(15, position + 1) if args[3] > args[5] else max(0, position - 1)
            smoke.nodes = [scroll, {'text': str(position)}] + ([target] if position == 12 else [])
        with patch.object(smoke, 'dump'), patch.object(smoke, 'shell', side_effect=swipe) as shell:
            self.assertIs(smoke.visible('deep-control'), target)
        self.assertLessEqual(shell.call_count, 15)

    def test_scroll_steps_overlap_so_a_short_metric_row_is_not_skipped(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        scroll = {'class': 'android.widget.ScrollView', 'bounds': '[30,100][1030,900]'}
        target = {'resource-id': 'metric', 'bounds': '[80,200][900,250]'}
        smoke.nodes = [scroll]
        def swipe(*args):
            self.assertLessEqual(abs(args[3] - args[5]), 400)
            smoke.nodes = [scroll, target]
        with patch.object(smoke, 'dump'), patch.object(smoke, 'shell', side_effect=swipe):
            self.assertIs(smoke.visible('metric'), target)

    def test_process_system_dialog_waits_without_closing_system_server(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        xml = '<hierarchy><node text="Process system isn\'t responding"/><node resource-id="android:id/aerr_close" bounds="[0,0][100,50]"/><node resource-id="android:id/aerr_wait" bounds="[0,50][100,100]"/></hierarchy>'
        with patch.object(smoke, 'shell', side_effect=['', xml, '', '<hierarchy/>']), patch.object(smoke, 'tap_node') as tap:
            smoke.dump()
        self.assertEqual(tap.call_args.args[0].get('resource-id'), 'android:id/aerr_wait')

    def test_our_app_anr_is_never_dismissed_as_system_dialog(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        xml = '<hierarchy><node text="밤길 지킴이 isn\'t responding"/><node resource-id="android:id/aerr_close" bounds="[0,0][100,50]"/><node resource-id="android:id/aerr_wait" bounds="[0,50][100,100]"/></hierarchy>'
        with patch.object(smoke, 'shell', side_effect=['', xml]), patch.object(smoke, 'tap_node') as tap:
            with self.assertRaisesRegex(AssertionError, 'Application ANR/crash'):
                smoke.dump()
        tap.assert_not_called()

    def test_scroll_starts_in_gutter_outside_full_width_buttons(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        scroll = {'class': 'android.widget.ScrollView', 'bounds': '[30,100][1030,900]'}
        target = {'resource-id': 'control', 'bounds': '[80,200][900,250]'}
        def swipe(*args):
            smoke.nodes = [scroll, target]
        smoke.nodes = [scroll]
        with patch.object(smoke, 'dump'), patch.object(smoke, 'shell', side_effect=swipe) as shell:
            self.assertIs(smoke.visible('control'), target)
        self.assertEqual(shell.call_args.args[2], 42)

    def test_click_refreshes_bounds_after_scrolling_settles(self):
        smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
        stale = {'resource-id': 'control', 'bounds': '[0,0][100,50]'}
        settled = {'resource-id': 'control', 'bounds': '[0,100][100,150]'}
        smoke.nodes = [settled]
        with patch.object(smoke, 'visible', return_value=stale), patch.object(smoke, 'dump'), patch.object(smoke, 'tap_node') as tap, patch.object(integration_smoke.time, 'sleep'):
            smoke.click(id='control')
        tap.assert_called_once_with(settled)

    def test_failure_writes_dated_evidence_without_claiming_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            with patch.object(integration_smoke, 'ROOT', root), patch.object(integration_smoke.Smoke, 'run', side_effect=AssertionError('fixed UI failure')), patch.object(integration_smoke.Smoke, 'screenshot'), patch('sys.argv', ['integration_smoke.py']):
                with self.assertRaises(SystemExit):
                    integration_smoke.main()
            reports = list(root.glob('verification/android-*/failure.md'))
            self.assertEqual(len(reports), 1)
            text = reports[0].read_text(encoding='utf-8')
            self.assertIn('fixed UI failure', text)
            self.assertIn('Last updated:', text)
            self.assertNotIn('- PASS:', text)

    def test_screenshot_preserves_historical_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            old = root / 'verification' / 'integration-tmap.png'
            old.parent.mkdir()
            old.write_bytes(b'historical capture')
            with patch.object(integration_smoke, 'ROOT', root), patch.object(integration_smoke.time, 'sleep'):
                smoke = integration_smoke.Smoke('unused-adb', 'unused-device')
                with patch.object(smoke, 'command', return_value=b'new capture' * 2000):
                    smoke.screenshot('integration-tmap.png')
            self.assertEqual(old.read_bytes(), b'historical capture')

    def test_report_preserves_historical_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            old = root / 'verification' / 'integration-ui.md'
            old.parent.mkdir()
            old.write_text('Historical verification on 2026-10-16', encoding='utf-8')
            with patch.object(integration_smoke, 'ROOT', root), patch.object(integration_smoke.Smoke, 'run'), patch('sys.argv', ['integration_smoke.py']):
                integration_smoke.main()
            self.assertEqual(old.read_text(encoding='utf-8'), 'Historical verification on 2026-10-16')


if __name__ == '__main__':
    unittest.main()
