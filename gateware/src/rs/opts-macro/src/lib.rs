use proc_macro::*;

#[proc_macro_derive(OptionView, attributes(option))]
pub fn derive_option_view(input: TokenStream) -> TokenStream {
    let input = syn::parse_macro_input!(input as syn::DeriveInput);
    let struct_name = input.ident;

    // Collect all fields marked with #[option]
    let fields = if let syn::Data::Struct(data_struct) = &input.data {
        if let syn::Fields::Named(fields_named) = &data_struct.fields {
            fields_named
                .named
                .iter()
                .filter_map(|field| {
                    if field.attrs.iter().any(|attr| attr.path().is_ident("option")) {
                        field.ident.clone()
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
        } else {
            Vec::new()
        }
    } else {
        Vec::new()
    };

    let options = fields.iter().map(|f| quote::quote! { &self.#f });
    let options_mut = fields.iter().map(|f| quote::quote! { &mut self.#f });

    let expanded = quote::quote! {
        impl OptionView for #struct_name {
            fn selected(&self) -> Option<usize> {
                self.selected
            }
            fn set_selected(&mut self, s: Option<usize>) {
                self.selected = s;
            }
            fn options(&self) -> OptionVec {
                OptionVec::from_slice(&[#(#options),*]).unwrap()
            }
            fn options_mut(&mut self) -> OptionVecMut {
                let mut v = OptionVecMut::new();
                #(v.push(#options_mut).ok();)*
                v
            }
        }
    };
    expanded.into()
}

#[proc_macro_derive(OptionPage, attributes(screen))]
pub fn derive_option_page(input: TokenStream) -> TokenStream {
    let input = syn::parse_macro_input!(input as syn::DeriveInput);
    let struct_name = input.ident;

    // Extract fields marked with #[screen(...)]
    let screen_fields = if let syn::Data::Struct(data_struct) = &input.data {
        if let syn::Fields::Named(fields_named) = &data_struct.fields {
            fields_named
                .named
                .iter()
                .filter_map(|field| {
                    field.attrs.iter().find_map(|attr| {
                        if attr.path().is_ident("screen") {
                            let variant: syn::Expr = attr.parse_args().unwrap();
                            field.ident.as_ref().map(|ident| (variant, ident))
                        } else {
                            None
                        }
                    })
                })
                .collect::<Vec<_>>()
        } else {
            Vec::new()
        }
    } else {
        Vec::new()
    };

    // Generate match arms for `view` and `view_mut`
    let match_arms = screen_fields.iter().map(|(variant, ident)| {
        quote::quote! { #variant => &self.#ident }
    });
    let match_arms_mut = screen_fields.iter().map(|(variant, ident)| {
        quote::quote! { #variant => &mut self.#ident }
    });

    // Generate the final implementation
    let expanded = quote::quote! {
        impl OptionPage for #struct_name {
            fn modify(&self) -> bool { self.modify }
            fn modify_mut(&mut self, modify: bool) { self.modify = modify; }
            fn screen(&self) -> &dyn OptionTrait { &self.screen }
            fn screen_mut(&mut self) -> &mut dyn OptionTrait { &mut self.screen }
            fn view(&self) -> &dyn OptionView {
                match self.screen.value {
                    #(#match_arms),*
                }
            }
            fn view_mut(&mut self) -> &mut dyn OptionView {
                match self.screen.value {
                    #(#match_arms_mut),*
                }
            }
        }
    };

    expanded.into()
}
