"""Tennis Coach — standalone web server."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import math
import os
import sys

ROOT    = Path(__file__).resolve().parent
WEB_DIR = ROOT / 'web'
SRC_DIR = ROOT / 'src'

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/tennis-templates':
            try:
                from tennis_coach.templates import load_templates
                templates = load_templates()
                summary = {k: {'sample_count': v['sample_count'],
                               'angles': list(v['angles'].keys())}
                           for k, v in templates.items()}
                self._json(200, {'ok': True, 'templates': summary})
            except Exception as e:
                self._json(500, {'ok': False, 'error': str(e)})
        else:
            super().do_GET()

    def do_POST(self):
        routes = {
            '/api/tennis-keypoint':  self._handle_keypoint,
            '/api/tennis-train':     self._handle_train,
            '/api/tennis-evaluate':  self._handle_evaluate,
            '/api/tennis-compare':   self._handle_compare,
        }
        handler = routes.get(self.path)
        if handler:
            handler()
        else:
            self.send_error(404, 'Not Found')

    # ── helpers ──────────────────────────────────────────────

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(length))

    def _json(self, code, data):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        pass

    def _extract_keypoints(self, image_b64, provider='baidu'):
        if provider == 'mediapipe':
            from tennis_coach.mediapipe_keypoint import detect_keypoints_mediapipe
            parts = detect_keypoints_mediapipe(image_b64)
            if not parts:
                raise ValueError('MediaPipe 未检测到人体')
            return parts
        else:
            from tennis_coach.keypoint import detect_keypoints, parse_keypoints
            raw = detect_keypoints(image_b64)
            if 'error_code' in raw:
                raise ValueError(f"百度API错误: {raw.get('error_msg', raw)}")
            persons = parse_keypoints(raw)
            if not persons:
                raise ValueError('百度API未检测到人体')
            return persons[0]

    def _auto_match(self, student_angles, templates):
        best_action, best_score = None, float('inf')
        for action, tmpl in templates.items():
            shared = {k for k in student_angles if k in tmpl['angles']}
            if not shared:
                continue
            rmse = math.sqrt(
                sum((student_angles[k] - tmpl['angles'][k])**2 for k in shared) / len(shared))
            if rmse < best_score:
                best_score, best_action = rmse, action
        return best_action, best_score

    # ── endpoints ─────────────────────────────────────────────

    def _handle_keypoint(self):
        body = self._read_body()
        try:
            parts = self._extract_keypoints(body.get('image', ''),
                                             body.get('provider', 'baidu'))
            self._json(200, {'ok': True, 'persons': [parts]})
        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def _handle_train(self):
        body = self._read_body()
        action = body.get('action', '正手击球')
        try:
            from tennis_coach.keypoint import detect_keypoints, parse_keypoints
            from tennis_coach.analyzer import extract_angles
            from tennis_coach.templates import save_template
            raw = detect_keypoints(body['image'])
            if 'error_code' in raw:
                self._json(500, {'ok': False, 'error': f"百度API错误: {raw.get('error_msg')}"})
                return
            persons = parse_keypoints(raw)
            if not persons:
                self._json(200, {'ok': False, 'error': '未检测到人体'})
                return
            angles = extract_angles(persons[0])
            template = save_template(action, angles, 1)
            self._json(200, {'ok': True, 'action': action, 'angles': angles,
                             'sample_count': template['sample_count']})
        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def _handle_evaluate(self):
        body = self._read_body()
        mime = body.get('mime', 'image/jpeg')
        try:
            from tennis_coach.analyzer import extract_angles, evaluate
            from tennis_coach.templates import load_templates
            templates = load_templates()
            if not templates:
                self._json(200, {'ok': False, 'error': '还没有标准模板，请先训练'})
                return
            parts = self._extract_keypoints(body['image'], body.get('provider', 'baidu'))
            student_angles = extract_angles(parts)
            best_action, best_score = self._auto_match(student_angles, templates)
            if not best_action:
                self._json(200, {'ok': False, 'error': '无法匹配模板'})
                return
            report = evaluate(parts, templates[best_action], best_action)
            report['识别置信度'] = round(max(0, 100 - best_score), 1)
            report['VL语义分析'] = self._vl_analysis(body['image'], mime, best_action, report)
            self._json(200, {'ok': True, 'report': report, 'keypoints': parts})
        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def _handle_compare(self):
        body = self._read_body()
        mime = body.get('mime', 'image/jpeg')
        try:
            from tennis_coach.analyzer import extract_angles, evaluate
            from tennis_coach.templates import load_templates
            templates = load_templates()
            results = {}
            for provider in ('baidu', 'mediapipe'):
                try:
                    parts = self._extract_keypoints(body['image'], provider)
                    student_angles = extract_angles(parts)
                    best_action, best_score = self._auto_match(student_angles, templates)
                    if best_action:
                        report = evaluate(parts, templates[best_action], best_action)
                        report['识别置信度'] = round(max(0, 100 - best_score), 1)
                        results[provider] = {'ok': True, 'report': report, 'keypoints': parts}
                    else:
                        results[provider] = {'ok': False, 'error': '无法匹配模板（请先训练）'}
                except Exception as e:
                    results[provider] = {'ok': False, 'error': str(e)}
            self._json(200, {'ok': True, 'results': results})
        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def _vl_analysis(self, image_b64, mime, action, report):
        try:
            import requests as req
            from tennis_coach.keypoint import _get_access_token
            root = Path(__file__).resolve().parent
            env_path = root / '.env'
            api_key = None
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith('QIANWEN_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
            api_key = api_key or os.environ.get('QIANWEN_API_KEY')
            if not api_key:
                return None
            issues = '、'.join([f"{i['角度名称']}{i['方向']}"
                                for i in report.get('问题列表', [])]) or '无明显问题'
            prompt = (f"这是一张网球「{action}」动作照片。关节角度分析发现：{issues}。"
                      f"请补充分析：1.握拍方式 2.击球点位置 3.眼神头部 4.最重要改进建议。"
                      f"每点一句简洁中文，不要前缀。")
            resp = req.post(
                'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                headers={'Content-Type': 'application/json',
                         'Authorization': f'Bearer {api_key}'},
                json={'model': 'qwen-vl-max', 'messages': [{'role': 'user', 'content': [
                    {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_b64}'}},
                    {'type': 'text', 'text': prompt}
                ]}]},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip()
        except Exception:
            pass
        return None


if __name__ == '__main__':
    os.chdir(WEB_DIR)
    port = 8080
    print(f'Tennis Coach server at http://127.0.0.1:{port}')
    with ThreadingHTTPServer(('0.0.0.0', port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nShutting down')
