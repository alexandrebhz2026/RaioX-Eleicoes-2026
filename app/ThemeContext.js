import React,{createContext,useContext,useEffect,useMemo,useState} from 'react';
import {Appearance} from 'react-native';
import * as SecureStore from 'expo-secure-store';

export const THEME_KEY='raiox.theme.preference.v1';

const PALETTES={
  dark:{
    mode:'dark',bg:'#061329',surface:'#0B1D3A',surface2:'#0F2445',border:'#214D80',borderSoft:'#173B63',
    text:'#F7FBFF',muted:'#AFC0D8',blue:'#168CFF',cyan:'#1CCBFF',green:'#47D6A0',yellow:'#FFD166',danger:'#FF5A63',nav:'#07162C',input:'#091A34',shadow:'#000000'
  },
  light:{
    mode:'light',bg:'#F6F9FD',surface:'#FFFFFF',surface2:'#F0F5FB',border:'#D5E1EF',borderSoft:'#E7EEF7',
    text:'#091A34',muted:'#64748B',blue:'#1677FF',cyan:'#00A9E8',green:'#159F72',yellow:'#A96A00',danger:'#D9363E',nav:'#FFFFFF',input:'#F7FAFE',shadow:'#173B63'
  }
};

const ThemeContext=createContext({preference:'automatic',effective:'dark',theme:PALETTES.dark,setPreference:async()=>{}});

export function ThemeProvider({children}){
  const [preference,setPreferenceState]=useState('automatic');
  const [system,setSystem]=useState(Appearance.getColorScheme()==='light'?'light':'dark');
  useEffect(()=>{SecureStore.getItemAsync(THEME_KEY).then(v=>{if(['light','dark','automatic'].includes(v))setPreferenceState(v)}).catch(()=>{})},[]);
  useEffect(()=>{const sub=Appearance.addChangeListener(({colorScheme})=>setSystem(colorScheme==='light'?'light':'dark'));return()=>sub?.remove?.()},[]);
  const effective=preference==='automatic'?system:preference;
  const setPreference=async value=>{if(!['light','dark','automatic'].includes(value))return;setPreferenceState(value);try{await SecureStore.setItemAsync(THEME_KEY,value)}catch{}};
  const value=useMemo(()=>({preference,effective,theme:PALETTES[effective],setPreference}),[preference,effective]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(){return useContext(ThemeContext)}
