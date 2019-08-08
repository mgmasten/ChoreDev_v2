import { NgModule } from '@angular/core';
import { IonicModule } from 'ionic-angular';

import { GraphComponent } from './graph/graph';
import { ProfileCardComponent } from './profile-card/profile-card';
import { ScoreCardComponent } from './score-card/score-card';
import { BurgerNavComponent } from './burger-nav/burger-nav';
import { ChoreCardComponent } from './chore-card/chore-card';
import { ScoreComponent } from './score/score';

export const components = [
  GraphComponent,
  BurgerNavComponent,
  ScoreComponent
];

@NgModule({
  declarations: [components,
    ProfileCardComponent,
    ProfileCardComponent,
    ScoreCardComponent,
    ChoreCardComponent
  
    ],
  imports: [IonicModule],
  exports: [components,
    ProfileCardComponent,
    ProfileCardComponent,
    ScoreCardComponent,
    ChoreCardComponent,
    ]
})
export class ComponentsModule {}
