import { SharedModule } from '../../app/shared.module';
import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { CreateChorePage } from './create-chore';

@NgModule({
  declarations: [
    CreateChorePage,
  ],
  imports: [
    IonicPageModule.forChild(CreateChorePage),
    SharedModule
  ],
})
export class CreateChorePageModule {}
