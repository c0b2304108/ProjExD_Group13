import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん1p）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        self.img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.charge_time = 0  # チャージ時間を管理する変数を追加
        self.is_charging = False  # チャージ状態かどうか

        
        self.dire = (1, 0)
        self.image = self.img
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
    
    def start_charging(self):
        self.is_charging = True
        self.charge_time = 0  # チャージを開始するときにリセット

    def stop_charging(self):
        self.is_charging = False
        if self.charge_time > 50:  # チャージ時間が一定以上ならチャージショット発射
            return True  # チャージショット発射信号
        return False
    
    def draw_charge_effect(self, screen: pg.Surface):
        if self.is_charging:
            radius = min(50, self.charge_time)  # チャージ時間に応じた半径
            pg.draw.circle(screen, (255, 0, 255), self.rect.center, radius, 2)  # チャージエフェクト


    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        #pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) == (False, True):
            self.rect.move_ip(-self.speed*sum_mv[0], 0)
        if check_bound(self.rect) == (True, False):
            self.rect.move_ip(0, -self.speed*sum_mv[1])
        if check_bound(self.rect) == (False, False):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.img
        screen.blit(self.image, self.rect)
        self.draw_charge_effect(screen)
class Bird_2p(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん2p）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        self.img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.charge_time = 0  # チャージ時間を管理する変数を追加
        self.is_charging = False  # チャージ状態かどうか

        # self.imgs = {
        #     (-1, 0): img,
        #     (+1, 0): img,  # 右
        #     (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
        #     (-1, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
        #     (-2, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
        #     (-2, 0): img0,  # 左
        #     (-2, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
        #     (-1, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
        #     (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        # }
        self.dire = (1, 0)
        self.image = self.img
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def start_charging(self):
        self.is_charging = True
        self.charge_time = 0  # チャージを開始するときにリセット

    def stop_charging(self):
        self.is_charging = False
        if self.charge_time > 50:  # チャージ時間が一定以上ならチャージショット発射
            return True  # チャージショット発射信号
        return False
    
    def draw_charge_effect(self, screen: pg.Surface):
        if self.is_charging:
            radius = min(50, self.charge_time)  # チャージ時間に応じた半径
            pg.draw.circle(screen, (255, 0, 255), self.rect.center, radius, 2)  # チャージエフェクト


    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        #pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) == (False, True):
            self.rect.move_ip(-self.speed*sum_mv[0], 0)
        if check_bound(self.rect) == (True, False):
            self.rect.move_ip(0, -self.speed*sum_mv[1])
        if check_bound(self.rect) == (False, False):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.img
        screen.blit(self.image, self.rect)
        self.draw_charge_effect(screen)


class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: "Bird"):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 10

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, is_charge_shot = False):
        """
        ビーム画像Surfaceを生成する
        引数1 bird：ビームを放つこうかとん
        引数2 angle0：複数発射時の角度
        """
        super().__init__()
        self.vx, self.vy = 1,0
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        #self.rect = self.image.get_rect()
        self.speed = 10 if not is_charge_shot else 20 #通常ショットとチャージショットとの速さの違い
        self.damage = 1 if not is_charge_shot else 5  # チャージショットのダメージ
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery + bird.rect.height * self.vy 
        self.rect.centerx = bird.rect.centerx + bird.rect.width * self.vx 

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()        



class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy|Boss", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center =WIDTH, random.randint(100, HEIGHT-100)
        self.vx, self.vy = -6, 0
        self.bound = random.randint(50, HEIGHT//2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        self.rect.move_ip(self.vx, self.vy)

class Bomb_Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center =WIDTH-10, random.randint(100, HEIGHT-100)
        self.vx, self.vy = 0, 0
        self.state = "start"  # 降下状態or停止状態
        self.interval = 5  # 爆弾投下インターバル

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        self.state="stop"
        
class Super_Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    img = pg.image.load("fig/horse.png") 
    img = pg.transform.scale(img,(200,200))

    def __init__(self, hp:int):
        super().__init__()
        self.image = __class__.img
        #self.image = pg.Surface((100, 100))
        self.rect = self.image.get_rect()
        self.lifestate="alive"
        self.hp = hp
        self.rect.center =WIDTH, random.randint(100, HEIGHT-100)
        self.vx, self.vy = -20, 0
        self.state = "stop"  # 降下状態or停止状態
        self.interval = 50  # 爆弾投下インターバル
        self.count = 0

    def update(self):
        self.count+=1
        print(self.count)
        if self.count>=self.interval:
            self.rect.move_ip(self.vx, self.vy)

    def damage(self):
        
        self.hp-=1
        if self.hp<=0:
            self.lifestate="dead"
            self.kill()
            

class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    

    def __init__(self, beams_group):
        super().__init__()
        self.beams_group = beams_group
        img = pg.image.load(f"fig/boss.png")
        self.img = pg.transform.flip(img, False, False)
        self.image = self.img
        self.rect = self.image.get_rect()
        self.rect.center =WIDTH, HEIGHT/2
        self.vx, self.vy = -3, 0
        self.bound = WIDTH - 300
        self.state = "moving"
        self.beam_interval = 100
        self.last_shot_time = 0
        self.health = 20

    def update(self, tmr):
        if self.state == "moving":
            self.rect.move_ip(self.vx, self.vy)
            if self.rect.centerx <= self.bound:
                self.vx = 0
                self.state = "stopped"

        if self.state == "stopped":
            if tmr - self.last_shot_time >= self.beam_interval:
                self.beams_group.add(BossBeam(self))
                self.last_shot_time = tmr


class BossBeam(pg.sprite.Sprite):
    def __init__(self, boss: Boss):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/boss_beam.png"), 0, 1.0)
        self.rect = self.image.get_rect()
        self.rect.centerx = boss.rect.centerx
        self.rect.centery = boss.rect.centery
        self.vx = -6

    def update(self):
        self.rect.move_ip(self.vx, 0)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)




class Item(pg.sprite.Sprite):
    """
    アイテムに関するクラス
    """
    def __init__(self, position: tuple[int, int]):
        """
        アイテムの初期設定
        引数1 position：アイテムが出現する座標
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("fig/sp.png"), 0, 0.5)
        self.rect = self.image.get_rect(center=position)
        self.spawn_time = pg.time.get_ticks()  # 出現した時刻を記録

    def update(self):
        """
        アイテムが10秒経過したら消える
        """
        if pg.time.get_ticks() - self.spawn_time > 10000:  # 10秒経過で消える
            self.kill()

def game_over(screen): #ゲームオーバー時の画面
    bo =pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(bo, (0,0,0), pg.Rect(0,0,WIDTH,HEIGHT))
    bo.set_alpha(155)
    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 350, 350
    kk2_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk2_rct = kk2_img.get_rect()
    kk2_rct.center = 780, 350
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("GAME OVER", True, (255, 255, 255))
    screen.blit(bo, [0, 0])
    screen.blit(txt, [400, HEIGHT/2])
    screen.blit(kk_img,kk_rct)
    screen.blit(kk2_img,kk2_rct)
    pg.display.update()
    time.sleep(5)


def main():

    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    clock  = pg.time.Clock()
    tmr=0
    bg_tmr=0
    score = Score()
    bird = Bird(3, (300, 200))
    bird_2p = Bird_2p(10, (300, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    boss = pg.sprite.Group()
    boss_beams = pg.sprite.Group()
    b_emys = pg.sprite.Group()
    sp_emys = pg.sprite.Group()
    items = pg.sprite.Group()  # アイテム用のグループ
    enemy_count = 0  # 敵を倒した数をカウント

        
    



    while True:
        #screen.blit(bg_img,[0,0])

        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                bird.start_charging()  # スペースキーを押したらチャージ開始
            if event.type == pg.KEYUP and event.key == pg.K_SPACE:
                if bird.stop_charging():  # チャージが一定時間以上ならチャージショット発射
                    beams.add(Beam(bird, is_charge_shot=True))
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird_2p.start_charging()  # 左シフトキーを押したらチャージ開始
            if event.type == pg.KEYUP and event.key == pg.K_LSHIFT:
                if bird_2p.stop_charging():  # チャージが一定時間以上ならチャージショット発射
                    beams.add(Beam(bird_2p, is_charge_shot=True))
            
        if bird.is_charging:
            bird.charge_time += 1
        else:
            if tmr%50==0:
                beams.add(Beam(bird))

        if bird_2p.is_charging:
            bird_2p.charge_time += 1
        else:
            if tmr%50==0:
                beams.add(Beam(bird_2p))


        x = -(bg_tmr%3200)
        screen.blit(bg_img, [x, 0])
        screen.blit(pg.transform.flip(bg_img,True,False), [x+1600, 0])
        screen.blit(bg_img, [x+3200, 0])
        screen.blit(pg.transform.flip(bg_img,True,False), [x+4800, 0])

        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        if tmr/600 == 1:
            boss.add(Boss(boss_beams))

        if tmr%200 == 0:
            sp_emys.add(Super_Enemy(2))

        if tmr%300 == 0:
            b_emys.add(Bomb_Enemy())

        for b_emy in b_emys:
            if b_emy.state == "stop" and tmr%b_emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(b_emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            enemy_count += 1  # 敵を倒した数を増やす


            # 5体倒すごとにアイテムをドロップ
            if enemy_count % 5 == 0:
                items.add(Item(emy.rect.center))

        for b_emy in pg.sprite.groupcollide(b_emys, beams, True, True).keys():
            exps.add(Explosion(b_emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
        
        
        for sp_emy in pg.sprite.groupcollide(sp_emys, beams , False, True).keys():
            sp_emy.damage()
            if sp_emy.lifestate == "dead":
                exps.add(Explosion(sp_emy, 100))
                score.value += 50

        for b_emy in pg.sprite.groupcollide(b_emys, beams, True, True).keys():
            exps.add(Explosion(b_emy, 100))  # 爆発エフェクト
            score.value += 10  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
        
        
        for sp_emy in pg.sprite.groupcollide(sp_emys, beams , False, True).keys():
            sp_emy.damage()
            if sp_emy.lifestate == "dead":
                exps.add(Explosion(sp_emy, 100))
                score.value += 50

        #[Bomb(emy, bird),Bomb(emy, bird),Bomb(emy, bird)......]
        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.value += 1  # 1点アップ
        if pg.sprite.spritecollide(bird, items, True):
            bird.speed += 5  # スピードアップ効果
        if len(pg.sprite.spritecollide(bird, emys, True)) != 0 or len(pg.sprite.spritecollide(bird, sp_emys, True)) != 0 or len(pg.sprite.spritecollide(bird, b_emys, True)) != 0:
            game_over(screen)
            return
        
        if len(pg.sprite.spritecollide(bird_2p, emys, True)) != 0:
            game_over(screen)
            return
        for boss_hit in pg.sprite.groupcollide(boss, beams, False, True).keys():
            for beam in beams:
                if beam.rect.colliderect(boss_hit.rect):
                    exps.add(Explosion(beam, 100))
                    beam.kill()
            boss_hit.health -= 1
            if boss_hit.health <= 0:
                exps.add(Explosion(boss_hit, 100))
                score.value += 100
                boss_hit.kill()
                bird.change_img(6, screen)

                font = pg.font.Font(None, 80)
                clear_text = font.render("GAME CLEAR!", True, (0, 255, 0))
                text_rect = clear_text.get_rect(center = (WIDTH // 2, HEIGHT // 2))
                screen.blit(clear_text, text_rect)
                pg.display.update()
                time.sleep(3)
                return

        if len(pg.sprite.spritecollide(bird, emys, True)) != 0:
            game_over(screen)
            return
        if pg.sprite.spritecollide(bird, boss_beams, True):
            bird.change_img(8, screen)
            score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        
        
        
        bird.update(key_lst, screen)
        bird_2p.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        b_emys.update()
        b_emys.draw(screen)
        sp_emys.update()
        sp_emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        boss.update(tmr)
        boss_beams.update()
        boss_beams.draw(screen)
        boss.draw(screen)
        items.update()  # アイテムの更新（時間経過チェック）
        items.draw(screen)  # アイテムの描画
        score.update(screen)
        
        pg.display.update()
        tmr += 1
        bg_tmr +=4
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
