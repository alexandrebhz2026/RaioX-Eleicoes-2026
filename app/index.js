import React from 'react';
import {SafeAreaView, StyleSheet, Text, View} from 'react-native';
import {registerRootComponent} from 'expo';
import AuthGate from './AuthGate';

const NAVY='#061329', WHITE='#F7FBFF', MUTED='#B4C2D7', CYAN='#20D0F2';
let AppComponent=null;

function StartupFallback({error}){
  return <SafeAreaView style={s.safe}><View style={s.center}>
    <Text style={s.brand}>RAIO-X <Text style={{color:CYAN}}>ELEIÇÕES 2026</Text></Text>
    <Text style={s.title}>O aplicativo abriu em modo seguro.</Text>
    <Text style={s.text}>Uma parte da interface não pôde ser carregada. Feche e abra novamente. Se continuar, envie uma foto desta tela para corrigirmos sem perder seus dados.</Text>
    {!!error&&<Text style={s.code}>{String(error?.message||error).slice(0,180)}</Text>}
  </View></SafeAreaView>;
}

class StartupBoundary extends React.Component{
  constructor(props){super(props);this.state={error:null}}
  static getDerivedStateFromError(error){return {error}}
  componentDidCatch(error,info){console.error('RAIO-X startup boundary',error,info)}
  render(){return this.state.error?<StartupFallback error={this.state.error}/>:this.props.children}
}

function SafeApp(){
  try{
    if(!AppComponent)AppComponent=require('./App').default;
    if(!AppComponent)throw new Error('APP_MODULE_EMPTY');
    return <AppComponent/>;
  }catch(error){
    console.error('RAIO-X App module load failed',error);
    return <StartupFallback error={error}/>;
  }
}

function Root(){
  return <StartupBoundary><AuthGate><SafeApp/></AuthGate></StartupBoundary>;
}

const s=StyleSheet.create({
  safe:{flex:1,backgroundColor:NAVY},center:{flex:1,justifyContent:'center',padding:24},brand:{color:WHITE,fontSize:26,fontWeight:'900'},title:{color:WHITE,fontSize:20,fontWeight:'900',marginTop:20},text:{color:MUTED,fontSize:15,lineHeight:22,marginTop:10},code:{color:'#FFD166',fontSize:11,lineHeight:16,marginTop:18}
});

registerRootComponent(Root);
