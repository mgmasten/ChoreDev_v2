// Global state (used for theming)
import { AppState } from './app.global';

// Providers
import { ToastService } from '../providers/util/toast.service';
import { UserService } from '../providers/util/user.service';
import { AlertService } from '../providers/util/alert.service';

// Ionic native providers
import { Diagnostic } from '@ionic-native/diagnostic';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

// Directives

// Modules
import { SwingModule } from 'angular2-swing';
import { BrowserModule } from '@angular/platform-browser';
import { HttpModule } from '@angular/http';

export const MODULES = [
  SwingModule,
  BrowserModule,
  HttpModule,
];

export const PROVIDERS = [
  AlertService,
  ToastService,
  AppState,
  UserService,
  Diagnostic,
  // Ionic native specific providers
  StatusBar,
  SplashScreen
];

export const DIRECTIVES = [

];
