use proc_macro::*;

#[proc_macro_derive(OptionView, attributes(option))]
pub fn derive_option_view(input: TokenStream) -> TokenStream {
    let input = syn::parse_macro_input!(input as syn::DeriveInput);
    let struct_name = input.ident;

    // Extract fields marked with #[option(...)]
    let fields = if let syn::Data::Struct(data_struct) = &input.data {
        if let syn::Fields::Named(fields_named) = &data_struct.fields {
            fields_named
                .named
                .iter()
                .filter_map(|field| {
                    if let Some(attr) = field.attrs.iter().find(|a| a.path().is_ident("option")) {
                        let args = attr.parse_args_with(syn::punctuated::Punctuated::<syn::Expr, syn::Token![,]>::parse_terminated).unwrap();
                        field.ident.as_ref().map(|ident| (ident, &field.ty, args))
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

    // Generate code for `options` and `options_mut`
    let options = fields.iter().map(|(ident, _, _)| quote::quote! { &self.#ident });
    let options_mut = fields.iter().map(|(ident, _, _)| quote::quote! { &mut self.#ident });

    // Generate the `Default` implementation
    let default_fields = fields.iter().map(|(ident, ty, args)| {
        if is_num_option(ty) {
            // NumOption: #[option(value, step, min, max)]
            if args.len() != 4 {
                panic!("Expected 4 arguments for NumOption in #[option(...)]");
            }
            let value = &args[0];
            let step = &args[1];
            let min = &args[2];
            let max = &args[3];
            quote::quote! {
                #ident: NumOption {
                    name: String::from_str(stringify!(#ident)).unwrap(),
                    value: #value,
                    step: #step,
                    min: #min,
                    max: #max,
                }
            }
        } else if is_enum_option(ty) {
            // EnumOption: #[option(default_value)]
            if args.len() != 1 {
                panic!("Expected 1 argument for EnumOption in #[option(...)]");
            }
            let value = &args[0];
            quote::quote! {
                #ident: EnumOption {
                    name: String::from_str(stringify!(#ident)).unwrap(),
                    value: #value,
                }
            }
        } else {
            panic!("Unsupported type for #[option(...)]");
        }
    });

    // Generate the final implementation
    let expanded = quote::quote! {
        impl OptionView for #struct_name {
            fn selected(&self) -> Option<usize> {
                self.selected
            }
            fn set_selected(&mut self, s: Option<usize>) {
                self.selected = s;
            }
            fn options(&self) -> OptionVec {
                let mut vec = OptionVec::new();
                #(vec.push(#options).unwrap_or_else(|_| panic!("Failed to push option"));)*
                vec
            }
            fn options_mut(&mut self) -> OptionVecMut {
                let mut vec = OptionVecMut::new();
                #(vec.push(#options_mut).unwrap_or_else(|_| panic!("Failed to push option"));)*
                vec
            }
        }

        impl Default for #struct_name {
            fn default() -> Self {
                Self {
                    selected: None,
                    #(#default_fields,)*
                }
            }
        }
    };

    expanded.into()
}

// Helper function to check if a type is `NumOption<T>`
fn is_num_option(ty: &syn::Type) -> bool {
    if let syn::Type::Path(type_path) = ty {
        if let Some(segment) = type_path.path.segments.last() {
            segment.ident == "NumOption"
        } else {
            false
        }
    } else {
        false
    }
}

// Helper function to check if a type is `EnumOption<T>`
fn is_enum_option(ty: &syn::Type) -> bool {
    if let syn::Type::Path(type_path) = ty {
        if let Some(segment) = type_path.path.segments.last() {
            segment.ident == "EnumOption"
        } else {
            false
        }
    } else {
        false
    }
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
