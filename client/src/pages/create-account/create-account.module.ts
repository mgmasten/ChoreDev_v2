import { SharedModule } from '../../app/shared.module';
import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { CreateAccountPage } from './create-account';

@NgModule({
  declarations: [
    CreateAccountPage,
 
  ],
  imports: [
    IonicPageModule.forChild(CreateAccountPage),
    SharedModule
  ],
})
export class CreateAccountPageModule {}
