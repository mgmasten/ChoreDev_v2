import { AppState } from './app.global';
import { Component, ViewChild } from '@angular/core';
import { Nav, Platform, MenuController } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { Subject } from 'rxjs/Subject';

import { UserService } from '../providers/util/user.service';
import { ToastService } from '../providers/util/toast.service';

@Component({
  templateUrl: 'app.html'
})
export class MyApp {
  @ViewChild(Nav) nav: Nav;

  rootPage: any = 'HomePage';
  activePage = new Subject();

  pages: Array<{ title: string, component: any, active: boolean, icon: string, requiresLogin: boolean, hideOnLogin?: boolean }>;
  customPages: any;
  rightMenuItems: Array<{ icon: string, active: boolean }>;
  state: any;
  placeholder = 'assets/img/avatar/girl-avatar.png';
  chosenPicture: any;

  constructor(
    public platform: Platform,
    public statusBar: StatusBar,
    public splashscreen: SplashScreen,
    public global: AppState,
    public menuCtrl: MenuController,
    public userService: UserService,
    public toastService: ToastService
  ) {
    this.initializeApp();
    this.rightMenuItems = [
      { icon: 'home', active: true },
      { icon: 'alarm', active: false },
      { icon: 'analytics', active: false },
      { icon: 'archive', active: false },
      { icon: 'basket', active: false },
      { icon: 'body', active: false },
      { icon: 'bookmarks', active: false },
      { icon: 'camera', active: false },
      { icon: 'beer', active: false },
      { icon: 'power', active: false },
    ];


    this.pages = [
      { title: 'Home', component: 'HomePage', active: true, icon: 'home', requiresLogin: false, hideOnLogin: false},
      { title: 'Invite', component: 'InvitePage', active: false, icon: 'map', requiresLogin: true },
      { title: 'Login', component: 'LoginPage', active: false, icon: 'map', requiresLogin: false , hideOnLogin: true},
      { title: 'Register', component: 'CreateAccountPage', active: false, icon: 'map', requiresLogin: false, hideOnLogin: true},
      { title: 'Create Chore', component: 'CreateChorePage', active: false, icon: 'map', requiresLogin: true },
      { title: 'Score', component: 'ScorePage', active: false, icon: 'map', requiresLogin: true},
      { title: 'Settings', component: 'SettingsPage', active: false, icon: 'map', requiresLogin: true }
    ];

    this.activePage.subscribe((selectedPage: any) => {
      this.pages.map(page => {
        page.active = page.title === selectedPage.title;
      });
    });
  }

  initializeApp() {
    this.platform.ready().then(() => {
      this.global.set('theme', '');
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      this.statusBar.styleDefault();
      this.splashscreen.hide();
      this.menuCtrl.enable(false, 'right');
    });
  }

  openPage(page) {
    // Reset the content nav to have just this page
    // we wouldn't want the back button to show in this scenario
    this.nav.setRoot(page.component);
    this.activePage.next(page);
  }

  rightMenuClick(item) {
    this.rightMenuItems.map(menuItem => menuItem.active = false);
    item.active = true;
  }

  logout() {
    this.userService.logout().then(response => {
      this.toastService.create('Logged out!');
      this.nav.setRoot('HomePage');
    }).catch(error => {
      this.toastService.create('Something went wrong logging out!');
    });
  }

  shouldDisplayMenuButton(page) {
    if (this.userService.loggedIn()) {
      return !page.hideOnLogin;
    } else {
      return !page.requiresLogin;
    }
  }
}
