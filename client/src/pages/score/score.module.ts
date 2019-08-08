import { SharedModule } from '../../app/shared.module';
import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ScorePage } from './score';

@NgModule({
  declarations: [
    ScorePage,
  ],
  imports: [
    IonicPageModule.forChild(ScorePage),
    SharedModule
  ],
})
export class ScorePageModule {
}
