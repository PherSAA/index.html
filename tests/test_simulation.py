"""Run: python -m unittest discover -s tests -v (requires Playwright and Chromium)."""
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / 'index.html').read_text()

class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={'width':1440,'height':900})
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.set_content(HTML)
        self.page.click('#pause')

    def tearDown(self):
        self.page.close()
        self.assertEqual(self.errors, [])

    def test_pause_resume_speed(self):
        p = self.page
        before = p.evaluate('JSON.stringify(cells)')
        p.wait_for_timeout(100)
        self.assertEqual(before, p.evaluate('JSON.stringify(cells)'))
        p.locator('#speed').fill('3'); p.locator('#speed').dispatch_event('input')
        self.assertEqual(p.locator('#speedLabel').inner_text(), '3×')
        self.assertEqual(p.evaluate('speed'), 3)
        p.click('#pause'); p.wait_for_timeout(100)
        self.assertNotEqual(before, p.evaluate('JSON.stringify(cells)'))
        self.assertEqual(p.locator('#pause').get_attribute('aria-pressed'), 'false')

    def test_population_and_reset(self):
        for count in ['100','300','600','1000','2000']:
            self.page.select_option('#amount', count)
            self.assertEqual(self.page.evaluate('cells.length'), int(count))
        self.page.evaluate('events=10;selected=cells[0];camera.x=100')
        self.page.click('#reset')
        self.assertEqual(self.page.evaluate('[events,selected,camera.x,paused]'), [0,None,0,True])

    def test_exact_overlap_exchanges_without_destroying_identity(self):
        result = self.page.evaluate('''() => {
          cells=[createCell(1),createCell(2)];const refs=[...cells];
          for(const c of cells){c.x=800;c.y=500;c.vx=c.vy=0;c.r=8;}
          cells[0].genes.fill(0);cells[1].genes.fill(200);events=0;update();
          return {distance:Math.abs(cells[0].x-cells[1].x),same:cells.every((c,i)=>c===refs[i]),events,genes:[cells[0].genes[3],cells[1].genes[3]],knowledge:cells.map(c=>c.knowledge)};
        }''')
        self.assertGreater(result['distance'], 0)
        self.assertEqual(result['genes'], [50,150])
        self.assertEqual(result['knowledge'], [1,1])
        self.assertTrue(result['same']);self.assertEqual(result['events'], 1)

    def test_population_bounds_and_gene_range_after_300_steps(self):
        self.page.select_option('#amount','2000')
        self.assertTrue(self.page.evaluate('''() => {
          const original=[...cells];for(let i=0;i<300;i++)update(3);
          return cells.length===2000&&cells.every((c,i)=>c===original[i]&&c.id===i+1&&Number.isFinite(c.x+c.y+c.vx+c.vy)&&c.x>=c.r&&c.x<=WORLD_W-c.r&&c.y>=c.r&&c.y<=WORLD_H-c.r&&c.genes.length===8&&c.genes.every(g=>g>=0&&g<=255));
        }'''))

    def test_benchmark_preserves_live_state_and_yields(self):
        p=self.page
        before=p.evaluate('JSON.stringify({cells,events,comparisons,paused})')
        p.evaluate("window.benchTicks=0;window.tickTimer=setInterval(()=>window.benchTicks++,0)")
        p.click('#bench'); p.wait_for_function("!document.getElementById('bench').disabled")
        self.assertEqual(before,p.evaluate('JSON.stringify({cells,events,comparisons,paused})'))
        self.assertGreater(p.evaluate('window.benchTicks'),2)
        self.assertIn('300 pasos',p.locator('#benchmark').inner_text())
        p.evaluate('clearInterval(window.tickTimer)')

    def test_selection_drag_cancel_and_center(self):
        p=self.page;p.evaluate('cells=[createCell(1)];cells[0].x=800;cells[0].y=500')
        box=p.locator('#world').bounding_box(); x=box['x']+box['width']/2;y=box['y']+box['height']/2
        p.mouse.click(x,y);self.assertEqual(p.evaluate('selected.id'),1)
        p.locator('#world').click(position={'x':5,'y':5});self.assertIsNone(p.evaluate('selected'))
        p.mouse.move(x,y);p.mouse.down()
        p.mouse.move(x+40,y+20,steps=30)
        self.assertTrue(p.evaluate('drag.moved'));self.assertNotEqual(p.evaluate('camera.x'),0)
        p.locator('#world').dispatch_event('pointercancel',{'pointerId':1})
        self.assertIsNone(p.evaluate('drag'));p.mouse.up();p.click('#center')
        self.assertEqual(p.evaluate('[camera.x,camera.y]'),[0,0])

    def test_responsive_layout_and_touch(self):
        for width,height in [(320,568),(390,844),(844,390),(1440,900)]:
            with self.subTest(viewport=(width,height)):
                p=self.page;p.set_viewport_size({'width':width,'height':height});p.wait_for_timeout(50)
                self.assertTrue(p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                for control in ['pause','reset','center','bench','amount','speed']:
                    self.assertGreaterEqual(p.locator('#'+control).bounding_box()['height'],44)
        context=self.browser.new_context(viewport={'width':390,'height':844},device_scale_factor=3,is_mobile=True,has_touch=True)
        p=context.new_page();p.set_content(HTML);p.tap('#pause')
        p.evaluate('cells=[createCell(1)];cells[0].x=800;cells[0].y=500')
        p.locator('#world').tap();self.assertEqual(p.evaluate('selected.id'),1)
        self.assertEqual(p.evaluate('canvas.width'),p.evaluate('Math.floor(canvas.clientWidth*2)'))
        context.close()

if __name__ == '__main__':
    unittest.main()
